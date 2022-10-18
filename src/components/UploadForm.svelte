<script>
    import {createEventDispatcher} from 'svelte'
    import {uploadForm} from '../store'
    import {slide} from 'svelte/transition'
    let files = null
    let value = ''
    const d = createEventDispatcher()
    let form 

    function submit() {
        if(files === null || !form) return
        $uploadForm = new FormData(form)
        d('submit');
        files = null;
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
        border: 0;
        outline: 0;
        padding: 1em 0;
        margin: 0;
        flex-grow: 1;
    }

    strong{
        padding: 1em;
    }

    div{
        padding: 1em 0;
    }
</style>


<div in:slide={{delay:300}} out:slide>
    <strong>Upload Files</strong>
    <form bind:this="{form}" on:submit|preventDefault>
            <label for="upload" class="sr">Select Files</label>
            <input type="file" multiple name="files" id="upload" bind:files bind:value>
            <button class=btn on:click="{submit}" disabled={!files}>Upload</button>
    </form>
</div>