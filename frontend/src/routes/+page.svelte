<script>
	import {
		Mic,
		Square,
		Copy,
		Check,
		Flag
	} from '@lucide/svelte';

	let question = $state('');
	let answer = $state('');
	let sources = $state([]);
	let regulationsVersion = $state('');

	let loading = $state(false);
	let warmingUp = $state(false);

	let listening = $state(false);
	let voiceSupported = $state(true);
	let voiceError = $state('');

	let copied = $state(false);

	let reporting = $state(false);
	let reportComment = $state('');
	let reportSubmitted = $state(false);
	let reportError = $state('');
	let submittingReport = $state(false);

	let recognition;


	// -------------------------
	// Voice input
	// -------------------------

	function startVoiceInput() {

		voiceError = '';

		const SpeechRecognition =
			window.SpeechRecognition ||
			window.webkitSpeechRecognition;

		if (!SpeechRecognition) {

			voiceSupported = false;

			voiceError =
				'Voice input is not supported by this browser.';

			return;
		}

		if (listening) {

			recognition?.stop();

			return;
		}

		recognition = new SpeechRecognition();

		recognition.lang = 'en-NZ';
		recognition.interimResults = true;
		recognition.continuous = false;

		recognition.onstart = () => {

			listening = true;

		};

		recognition.onresult = (event) => {

			let transcript = '';

			for (
				let i = event.resultIndex;
				i < event.results.length;
				i++
			) {

				transcript +=
					event.results[i][0].transcript;
			}

			if (transcript.trim()) {

				question =
					transcript.trim();

			}
		};

		recognition.onerror = (event) => {

			console.error(
				'Speech recognition error:',
				event.error
			);

			if (event.error === 'not-allowed') {

				voiceError =
					'Microphone access was denied.';

			} else {

				voiceError =
					'Voice input failed. Please try again.';
			}

			listening = false;
		};

		recognition.onend = () => {

			listening = false;

		};

		recognition.start();
	}


	// -------------------------
	// Keyboard shortcuts
	// -------------------------

	function handleKeydown(event) {

		if (
			event.key === 'Enter' &&
			(event.metaKey || event.ctrlKey) &&
			!loading &&
			question.trim()
		) {

			event.preventDefault();

			ask();
		}
	}


	// -------------------------
	// Ask
	// -------------------------

	async function ask() {

		if (
			!question.trim() ||
			loading
		) {

			return;
		}

		loading = true;
		warmingUp = false;

		answer = '';
		sources = [];
		regulationsVersion = '';

		copied = false;

		reporting = false;
		reportComment = '';
		reportSubmitted = false;
		reportError = '';

		const timeout = setTimeout(() => {

			warmingUp = true;

		}, 8000);

		try {

			const response = await fetch(
				`${import.meta.env.VITE_API_URL}/ask?question=${encodeURIComponent(question)}`
			);

			if (!response.ok) {

				throw new Error(
					`Request failed with status ${response.status}`
				);
			}

			const data =
				await response.json();

			answer = data.answer.replace(/\*\*/g, '');
			sources = data.sources;
			regulationsVersion =
				data.regulations_version;

		} catch (err) {

			console.error(err);

			answer =
				'Something went wrong.';

			sources = [];
			regulationsVersion = '';

		} finally {

			clearTimeout(timeout);

			loading = false;
			warmingUp = false;
		}
	}


	// -------------------------
	// Copy answer
	// -------------------------

	async function copyAnswer() {

		try {

			await navigator.clipboard.writeText(
				answer
			);

			copied = true;

			setTimeout(() => {

				copied = false;

			}, 2000);

		} catch (err) {

			console.error(
				'Failed to copy answer:',
				err
			);
		}
	}


	// -------------------------
	// Report issue
	// -------------------------

	async function submitReport() {

		if (
			!reportComment.trim() ||
			submittingReport
		) {

			return;
		}

		submittingReport = true;
		reportError = '';

		try {

			const response = await fetch(
				`${import.meta.env.VITE_API_URL}/report`,
				{
					method: 'POST',

					headers: {
						'Content-Type':
							'application/json'
					},

					body: JSON.stringify({
						question,
						answer,
						sources,
						comment:
							reportComment
					})
				}
			);

			if (!response.ok) {

				throw new Error(
					'Report submission failed'
				);
			}

			reportSubmitted = true;
			reporting = false;
			reportComment = '';

		} catch (err) {

			console.error(err);

			reportError =
				'Something went wrong while submitting the report.';

		} finally {

			submittingReport = false;
		}
	}
</script>


<div class="container">

	<h1>WCA Regulations Assistant</h1>

	<p class="subtitle">
		Ask questions about the WCA Regulations and Guidelines.
	</p>


	<!-- Question input -->

	<div class="question-input">

		<textarea
			bind:value={question}
			placeholder="Ask a WCA regulations question..."
			onkeydown={handleKeydown}
			disabled={loading}
		></textarea>

		<button
			class="voice-button"
			class:recording={listening}
			type="button"
			onclick={startVoiceInput}
			disabled={
				loading ||
				!voiceSupported
			}
			aria-label={
				listening
					? 'Stop voice input'
					: 'Start voice input'
			}
			title={
				listening
					? 'Stop listening'
					: 'Dictate question'
			}
		>

			{#if listening}

				<Square
					size={18}
					strokeWidth={2}
				/>

			{:else}

				<Mic
					size={20}
					strokeWidth={2}
				/>

			{/if}

		</button>

	</div>


	<!-- Ask button -->

	<button
		class="ask-button"
		onclick={ask}
		disabled={
			loading ||
			!question.trim()
		}
	>

		{loading
			? 'Searching...'
			: 'Ask'}

	</button>


	<!-- Voice status -->

	{#if listening}

		<p class="voice-status">
			Listening...
		</p>

	{/if}


	{#if voiceError}

		<p class="voice-error">
			{voiceError}
		</p>

	{/if}


	<!-- Loading -->

	{#if loading}

		<p class="loading">
			Searching regulations...
		</p>

		{#if warmingUp}

			<p class="warming-up">
				This is taking longer than usual.
				The server may be starting up.
				Hang tight!
			</p>

		{/if}

	{/if}


	<!-- Answer -->

	{#if answer}

		<div class="answer">

			<div class="answer-header">

				<h2>Answer</h2>

				<button
					class="copy-button"
					onclick={copyAnswer}
					aria-label="Copy answer"
					title="Copy answer"
				>

					{#if copied}

						<Check
							size={16}
							strokeWidth={2}
						/>

						Copied

					{:else}

						<Copy
							size={16}
							strokeWidth={2}
						/>

						Copy

					{/if}

				</button>

			</div>


			<p>
				{answer}
			</p>


		{#if regulationsVersion}
	<p class="regulations-version">
		Based on the WCA Regulations effective
		<a
			href="https://www.worldcubeassociation.org/regulations/"
			target="_blank"
			rel="noopener noreferrer"
		>
			{regulationsVersion}.
		</a>
	</p>
{/if}


			<!-- Report -->

			{#if !reportSubmitted}

				<button
					class="report-button"
					onclick={() =>
						reporting = !reporting}
				>

					<Flag
						size={16}
						strokeWidth={2}
					/>

					{reporting
						? 'Cancel'
						: 'Report an issue'}

				</button>


				{#if reporting}

					<div class="report-form">

						<label
							for="report-comment"
						>
							What went wrong?
						</label>

						<textarea
							id="report-comment"
							bind:value={
								reportComment
							}
							placeholder="Tell us what seems incorrect about this answer..."
						></textarea>


						<button
							class="report-submit"
							onclick={
								submitReport
							}
							disabled={
								submittingReport ||
								!reportComment.trim()
							}
						>

							{submittingReport
								? 'Submitting...'
								: 'Submit report'}

						</button>


						{#if reportError}

							<p class="report-error">
								{reportError}
							</p>

						{/if}

					</div>

				{/if}


			{:else}

				<p class="report-success">
					Thanks! Your report has been submitted.
				</p>

			{/if}

		</div>


		<!-- Sources -->

		<div class="sources">

			<h2>Retrieved Regulations</h2>

			{#each sources as source}

				<details>

					<summary>

						<a
							href={`https://www.worldcubeassociation.org/regulations/#${source.id}`}
							target="_blank"
							rel="noopener noreferrer"
							onclick={(e) =>
								e.stopPropagation()}
						>
							{source.id}
						</a>

					</summary>

					<p>
						{source.text}
					</p>

				</details>

			{/each}

		</div>

	{/if}

</div>