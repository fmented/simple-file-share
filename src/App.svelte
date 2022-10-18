<script>
	import ListView from './components/ListView.svelte';
	import FloatingButtons from './components/FloatingButtons.svelte';
	import LocationBar from './components/LocationBar.svelte';
	import NewFolderForm from './components/NewFolderForm.svelte';
	import NewFolderNotifier from './components/NewFolderNotifier.svelte';
	import UploadForm from './components/UploadForm.svelte';
	import UploadNotifier from './components/UploadNotifier.svelte';
	let nf = false
	let up= false

	let list

	let form = null

</script>

<style>
	main{
		display: grid;
		grid-template-rows: auto 1fr;
		height: 100%;
		width: 100%;
	}

	div{
		overflow: auto;
		height: 100%;
	}
</style>

<main>
	<div>
		{#if up}
			<UploadNotifier 
				on:close={_=>up=false}
				on:success={_=>{
					up=false
					list.updateList()
				}}
			/>
		{/if}
		{#if nf}
			<NewFolderNotifier 
				on:close={_=>nf=false}
				on:success={_=>{
					nf=false
					list.updateList()
				}}
			/>
		{/if}

		{#if form==='upload'}
			<UploadForm on:submit={()=>{
				form = null
				up = true
			}}/>
			
			{:else if form==='create'}
			<NewFolderForm on:submit={()=>{
				form=null
				nf=true
			}}/>
		{/if}
		<LocationBar/>
	</div>
	<div>
		<ListView bind:this={list}/>
		<FloatingButtons
			on:showUploadForm={()=>{
				form = (form==='upload')? null: 'upload'
			}}

			on:showCreateFolderForm={()=>{
				form = (form==='create')? null: 'create'
			}}
		/>

	</div>
</main>
