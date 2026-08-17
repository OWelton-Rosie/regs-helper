<script>
	import {
		Copy,
		Check,
		Flag
	} from '@lucide/svelte';

	let {
		answer,
		question,
		sources,
		regulationsVersion,
		regulationsReleaseUrl
	} = $props();

	let copied = $state(false);

	let reporting = $state(false);
	let reportComment = $state('');
	let reportSubmitted = $state(false);
	let reportError = $state('');
	let submittingReport = $state(false);

	async function copyAnswer() {
		try {
			await navigator.clipboard.writeText(answer);

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
						comment: reportComment
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
				<Check size={16} strokeWidth={2} />
				Copied
			{:else}
				<Copy size={16} strokeWidth={2} />
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
				href={regulationsReleaseUrl}
				target="_blank"
				rel="noopener noreferrer"
			>
				{regulationsVersion}.
			</a>
		</p>
	{/if}

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

				<label for="report-comment">
					What went wrong?
				</label>

				<textarea
					id="report-comment"
					bind:value={reportComment}
					placeholder="Tell us what seems incorrect about this answer..."
				></textarea>

				<button
					class="report-submit"
					onclick={submitReport}
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