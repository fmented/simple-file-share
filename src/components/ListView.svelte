<script>
    import {type, misc} from '../icons.js'
    import {showHiddenFiles, uploadForm, newFolderForm} from '../store.js'
    import {flip} from 'svelte/animate'
    import { onMount } from 'svelte';   
    

    let data = []

    export async function updateList() {
        const res = await fetch('./?updateList=true')
        if(res.ok){
            data = await res.json()
        }
    }

    onMount(async ()=>{
        await updateList()
    })

    $: files = $showHiddenFiles? data : data.filter(i=>i.hidden==false)

    function is_streamable(txt){
        return txt?.startsWith('audio') || txt?.startsWith('video')
    }

</script>

<style>
    .con{
        display: flex;
        flex-direction: column;
        width: 100%;
        gap: 1em;
        padding-top: 1em;
    }

    a, a:visited{
        text-decoration: none;
        color: inherit;
    }

    .hidden{
        color: #777;
    }

    a:visited{
        font-style: italic;
    }

    .row{
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 1em;
        padding: 0 1em;
    }

    .row:last-of-type{
        margin-bottom: 1.5em;
    }

    .file{
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }



    :global(.row > .link svg){
        height: 3em;
        width: 3em;
    }

    :global(.download svg){
        height: 1.2em;
        width: 1.2em;
        fill: white;
    }

    .icon{
        width: max-content;
    }

    .display{
        font-size: 1.2em;
    }

    .link{
        display: flex;
        align-items: center;
        overflow: hidden;
        text-overflow: hidden;
        gap: 1em;
    }

    .download{
        align-self: center;
    }




</style>

<div class="con">
    {#each files as d (d)}
        <div class="row" animate:flip>
            <a href="{d.linkname}{is_streamable(d.type)?'?stream=true':''}" class="link" target="{$uploadForm ===null && $newFolderForm === null? '_self': '_blank'}" class:hidden={d.hidden}>
                <div class="icon">{@html type.guess(d.type)}</div>
                <div class="file">
                    <span class="display">{d.displayname}</span>
                    <small class="size">{d.size !== null? d.pretty_size: '-'}</small>
                </div>
            </a>
            {#if d.size != null}
                <a class="download" href="{d.linkname}" download="{d.linkname}">{@html misc.download}</a>    
            {/if}    
        </div>   
    {/each}
</div>