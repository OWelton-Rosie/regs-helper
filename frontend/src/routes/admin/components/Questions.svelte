<script>
	let {
		questions = [],
		loading = false
	} = $props();

	function formatDate(timestamp) {
		const date = new Date(timestamp);

		if (Number.isNaN(date.getTime())) {
			return timestamp;
		}

		return date.toLocaleString();
	}
</script>

<section class="admin-section">

	<div class="section-header">

		<h2>Recent Questions</h2>

		<span class="count">
			{questions.length}
		</span>

	</div>

	{#if loading}

		<p class="admin-muted">
			Loading questions...
		</p>

	{:else if questions.length === 0}

		<p class="admin-muted">
			No questions yet.
		</p>

	{:else}

		{#each questions as row}

			<details class="admin-item">

				<summary>
					{formatDate(row[0])}
				</summary>

				<div class="item-content">

					<div class="admin-field">

						<strong>IP Address</strong>

						<p>
							{row[1]}
						</p>

					</div>

					<div class="admin-field">

						<strong>Question</strong>

						<p>
							{row[2]}
						</p>

					</div>

					<div class="admin-field">

						<strong>Answer</strong>

						<p>
							{row[3]}
						</p>

					</div>

				</div>

			</details>

		{/each}

	{/if}

</section>