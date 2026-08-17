<script>
	let { sources = [] } = $props();
</script>

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