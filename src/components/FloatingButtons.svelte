<script>
    import { createEventDispatcher } from 'svelte';
    import {misc} from '../icons'
    import {newFolderForm, uploadForm, showHiddenFiles} from '../store'
    
    const d = createEventDispatcher()

    let active = false

    $: showHide = $showHiddenFiles? misc.hide: misc.show

    function showCreateFolderForm() {
        if($newFolderForm !== null) return 
        d('showCreateFolderForm')
        active = false
    }

    function showUploadForm() {
        if($uploadForm !== null) return
        d('showUploadForm')
        active = false
    }

    function toggleHiddenFiles() {
        $showHiddenFiles=!$showHiddenFiles
        localStorage.setItem('showHiddenFiles', $showHiddenFiles)
        active = false
    }
    
</script>

<style>
    .float{
        position: fixed;
        width: 3em;
        height: 3em;
        right: 1rem;
        bottom: 3.5rem;
        background-color: #39f;
        border-radius: 50%;
        display: grid;
        place-items: center;
        transition: translate .3s ease;
        cursor: pointer;
    }

    :global(.float > svg){
        width: 2em;
        height: 2em;
        fill:white;
        transition: rotate .3s ease;
    }

    :global(.plus.active svg){
        rotate: 135deg;
    }

    :global(.folder.active){translate: -125% -125%;}
    :global(.upload.active){translate: -125% 0%;}
    :global(.show-hide.active){translate: 0% -125%;}

</style>

<button title="{$showHiddenFiles?'Hide':'Show'} Hidden Files" 
    class="float show-hide" class:active on:click="{toggleHiddenFiles}">{@html showHide}
</button>
<button title="Create New Folder" class="float folder" class:active on:click="{showCreateFolderForm}" disabled={$newFolderForm!==null}>{@html misc.folder}</button>
<button title="Upload Files" class="float upload" class:active on:click="{showUploadForm}" disabled={$uploadForm!==null}>{@html misc.upload}</button>
<button title="{active ? 'Close':'Open'} Menu" class="float plus" class:active on:click="{()=>active=!active}">{@html misc.add}</button>