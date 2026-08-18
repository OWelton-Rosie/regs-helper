<script>
	let {
		loading = false,
		loadData
	} = $props();
</script>

<div class="admin-header">

	<div>

		<h2>Admin Panel</h2>

		<p class="admin-subtitle">
			View recent questions and reported responses.
		</p>

	</div>

	<button
		class="refresh-button"
		onclick={loadData}
		disabled={loading}
	>
		{loading
			? 'Refreshing...'
			: 'Refresh'}
	</button>

</div>