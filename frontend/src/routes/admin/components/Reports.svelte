<script>
	let {
		reports = [],
		loading = false
	} = $props();

	function formatDate(timestamp) {
		const date = new Date(timestamp);

		if (Number.isNaN(date.getTime())) {
			return timestamp;
		}

		return date.toLocaleString();
	}

	function parseSources(sources) {
		if (!sources) {
			return [];
		}

		try {
			return JSON.parse(sources);
		} catch {
			return [];
		}
	}
</script>

<section class="admin-section">

	<div class="section-header">

		<h2>Reports</h2>

		<span class="count">
			{reports.length}
		</span>

	</div>

	{#if loading}

		<p class="admin-muted">
			Loading reports...
		</p>

	{:else if reports.length === 0}

		<p class="admin-muted">
			No reports yet.
		</p>

	{:else}

		{#each reports as row}

			<details class="admin-item">

				<summary>

					<div class="item-summary">

						<strong>
							{formatDate(row[0])}
						</strong>

						<span>
							{row[4]}
						</span>

					</div>

				</summary>

				<div class="item-content">

					<div class="admin-field">

						<strong>Question</strong>

						<p>
							{row[1]}
						</p>

					</div>

					<div class="admin-field">

						<strong>Answer</strong>

						<p>
							{row[2]}
						</p>

					</div>

					<div class="admin-field">

						<strong>
							Retrieved Regulations
						</strong>

						{#if parseSources(row[3]).length}

							<ul>

								{#each parseSources(row[3]) as source}

									<li>

										<a
											href={`https://www.worldcubeassociation.org/regulations/#${source.id}`}
											target="_blank"
											rel="noopener noreferrer"
										>
											{source.id}
										</a>

									</li>

								{/each}

							</ul>

						{:else}

							<p class="admin-muted">
								No sources recorded.
							</p>

						{/if}

					</div>

					<div
						class="admin-field report-comment"
					>

						<strong>Report</strong>

						<p>
							{row[4]}
						</p>

					</div>

				</div>

			</details>

		{/each}

	{/if}

</section>