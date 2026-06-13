<script>
	import '../app.css';
	import Footer from '../lib/components/footer.svelte';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href="/assets/favicon.webp" />
</svelte:head>

{@render children()}
<Footer />
