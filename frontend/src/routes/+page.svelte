<script>
	import QuestionInput from '$lib/components/QuestionInput.svelte';
	import Answer from '$lib/components/Answer.svelte';
	import Sources from '$lib/components/Sources.svelte';


	// -------------------------
	// State
	// -------------------------

	let question = $state('');
	let answer = $state('');
	let sources = $state([]);

	let regulationsVersion = $state('');
	let regulationsReleaseUrl = $state('');

	let loading = $state(false);
	let warmingUp = $state(false);


	// -------------------------
	// Fallback detection
	// -------------------------

	const FALLBACK_ANSWER =
		'I could not find a clear regulation covering this.';


	let isFallback = $derived(
		answer === FALLBACK_ANSWER
	);


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
		regulationsReleaseUrl = '';


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


			// Keep the answer exactly as returned
			// by the API. Do not strip Markdown or
			// interpret HTML here.

			answer =
				data.answer ?? '';


			sources =
				data.sources ?? [];


			regulationsVersion =
				data.regulations_version ?? '';


			regulationsReleaseUrl =
				data.regulations_release_url ?? '';


		} catch (err) {

			console.error(
				'Failed to ask question:',
				err
			);


			answer =
				'Something went wrong.';


			sources = [];

			regulationsVersion = '';
			regulationsReleaseUrl = '';


		} finally {

			clearTimeout(timeout);

			loading = false;
			warmingUp = false;
		}
	}
</script>


<div class="container">

	<h1>
		WCA Regulations Assistant
	</h1>


	<p class="subtitle">
		Ask questions about the WCA Regulations and Guidelines.
	</p>


	<!-- Question input -->

	<QuestionInput
		bind:question
		{loading}
		{ask}
	/>


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

		<Answer
			{answer}
			{question}
			{sources}
			{regulationsVersion}
			{regulationsReleaseUrl}
			{isFallback}
		/>


		<Sources
			{sources}
		/>

	{/if}

</div>