<script>
	let question = $state('');
	let answer = $state('');
	let sources = $state([]);
	let loading = $state(false);
	let warmingUp = $state(false);

	async function ask() {

		loading = true;
		warmingUp = false;

		answer = '';
		sources = [];

		const timeout = setTimeout(() => {
			warmingUp = true;
		}, 8000);

		try {

			const response = await fetch(
				`${import.meta.env.VITE_API_URL}/ask?question=${encodeURIComponent(question)}`
			);

			const data = await response.json();

			answer = data.answer;
			sources = data.sources;

		} catch (err) {

			console.error(err);

			answer = 'Something went wrong.';
			sources = [];

		} finally {

			clearTimeout(timeout);

			loading = false;
			warmingUp = false;
		}
	}
</script>

<div class="container">

	<h1>WCA Regulations Assistant</h1>

	<p class="subtitle">
		Ask questions about the WCA Regulations and Guidelines.
	</p>


		<textarea
			bind:value={question}
			placeholder="Ask a WCA regulations question..."
		></textarea>

		<button onclick={ask}>
			Ask
		</button>


	{#if loading}

	<p class="loading">
		Searching regulations...
	</p>

	{#if warmingUp}
		<p class="warming-up">
			This is taking longer than usual. The server may be starting up. Hang tight!
		</p>
	{/if}

{/if}

	{#if answer}

		<div class="answer">

			<h2>Answer</h2>

			<p>
				{answer}
			</p>

		</div>

		<div class="sources">

			<h2>Retrieved Regulations</h2>

			{#each sources as source}

				<details>

					<summary>
	<a
		href={`https://www.worldcubeassociation.org/regulations/#${source.id}`}
		target="_blank"
		rel="noopener noreferrer"
		onclick={(e) => e.stopPropagation()}
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