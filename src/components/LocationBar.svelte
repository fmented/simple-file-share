<script>
    import {misc} from '../icons.js'

    const url = window.location.pathname.split('/').filter(i=>i).map(i=>decodeURIComponent(i))


    function getPath(index){
        let s =''
        for(let i =0; i<=index; i++){
            s+= `/${encodeURIComponent(url[i])}`
        }
        return s
    }

    let scroll
</script>

<style>



    .base{
        overflow-x: auto;
        background: #111;
        padding: .25em;
        padding-bottom: .5em;
        overflow-y: hidden;
        white-space: nowrap;
    }    


    .loc{
        display: flex;
        align-items: center;
        justify-content: flex-start;
    }

    strong{
        font-size: 1em;
    }


    a{
        text-decoration: none;
        vertical-align: 0;
        padding: 0 .5em;
    }

    :global(.loc svg){
        width: 1em;
        height: 1em;
        vertical-align: -.25em;
        fill: white;
    }
</style>

<svelte:window bind:scrollY="{scroll}"/>

<div class="base" class:fixed={scroll>20}>
    <div class="loc">
        <strong>
            <a href="/">/</a>
            <span>{@html misc.arrow}</span>         
        </strong>
        {#each url as u, i}
            <strong>
                <a href="{window.location.origin}{getPath(i)}">{u}</a>
            {#if i !== url.length-1}
                <span>{@html misc.arrow}</span>         
            {/if}
            </strong>
        {/each}
    </div>
</div>
