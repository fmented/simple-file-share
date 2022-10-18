<script>
    import {createEventDispatcher} from 'svelte'
    import {newFolderForm} from '../store'
    import {slide} from 'svelte/transition'
    let value = ''
    const d = createEventDispatcher()
    let form 

    function submit() {
        if(!form) return
        $newFolderForm = new FormData(form)
        d('submit');
        value=''
    }

</script>

<style>
    form{
        display: flex;
        align-items: center;
        width: 100%;
        padding: 1em;
        padding-top: 0;
        padding-bottom: 0;
        gap: 1em;

    }


    input{
        padding: .5em;
        margin: 0;
        flex-grow: 1;
    }

    strong{
        padding: 1em
    }

    div{
        padding: 1em 0;
    }
</style>

<div in:slide={{delay:300}} out:slide>
    <strong>Create Folder</strong>
    <form bind:this="{form}" on:submit|preventDefault>
        <label for="name" class="sr">Folder Name</label>
        <input type="text" multiple name="name" id="name" bind:value>
        <button class=btn on:click="{submit}" disabled={!value}>Create</button>
    </form>
</div>