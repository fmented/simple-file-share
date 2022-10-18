<script>
    import {uploadForm} from '../store'
    import {createEventDispatcher} from 'svelte'
    import {misc} from '../icons'
    import {slide} from 'svelte/transition'
    import {tweened} from 'svelte/motion'
    import {cubicInOut} from 'svelte/easing'

    let message = `Uploading...`
    let progress = tweened(0, {duration:300, easing:cubicInOut})
    const d = createEventDispatcher()
    let status = ''
    let expand = false;

    const request = new XMLHttpRequest()
    request.open('post', './?upload=true')
    request.timeout = 3600000
    
    request.onreadystatechange = () => {
        if(request.readyState === XMLHttpRequest.DONE) {
            progress.set(100)
            $uploadForm = null

            if(request.status === 201){
                message = 'Success'
                status = 'success'
                return d('success')
            }

            if(request.status === 0){
                message = 'Connection failed'
                status = 'failed'
            }

        }
    }
    
    request.upload.onprogress = e => {
        message =  e.loaded === e.total ?'Saving...' : 'Uploading...'
        progress.set(Math.floor(100*e.loaded/e.total))
    }
  
    request.send($uploadForm)

    $: filenames = ($uploadForm?.getAll('files')||[]).map(v => v.name)

</script>

<style>
    
:global(.notifier-btn>svg){
    height: 1.5em;
    width: 1.5em;
    transition: rotate .3s ease;
    fill: white;
}

.con{
    width: 100%;
    position: relative;
    padding-left: 1em;
    margin-top: 1em;
}



:global(.expand svg){
    rotate: -90deg;
}

:global(.collapse svg){
    rotate: 90deg;
}

progress{
    height: 3em;
    position: relative;
    accent-color: #39f;
    margin: 0;
}

progress.success{
    accent-color: #3f9;
}

progress.failed{
    accent-color: #f45;
}

.filelist{
    overflow: auto;
    padding: .5em;
    margin: 0;
    border: 1px solid #aaa;
    margin-top: .5em;
    white-space: nowrap;
}

:global(.filelist li){
    list-style: none;
    padding: .25em 0;
    margin: 0;
    font-size: small;
}

.notifier-panel>*{
    width: 100%;
}

.con>.notifier-panel{
    width: calc(100% - 3em);
    display: grid;
    grid-template-rows: auto 1fr auto;
    max-height: 30vh;
}

.con>.notifier-btn{
    position: absolute;
    display: grid;
    place-items: center;
    width: 2em;
    right: .5em;
    top: 0;
    text-align: center;
    height: 100%;
    cursor: pointer;
}

.notifier-panel span, .notifier-panel a, .notifier-panel a:hover, .notifier-panel button{
    margin-top: .5em;
    text-align: center;
    border-radius: 0;
    margin-bottom: 0;
}

.action{
    display: flex;
}

.action > *{
    flex-grow: 1;
}
</style>

<div class="con" out:slide in:slide={{delay:300}}>
    <div class="notifier-panel">
        <strong title="Files Upload">Upload Files</strong>
        {#if expand}
            <div class="action" transition:slide>
                {#if status==='success'}
                    <a class="btn" href="./" title="Refresh the page">Refresh</a>
                    {:else}
                    <span class="btn">{message}</span>
                {/if}
                <button disabled={!status} on:click={()=>d('close')} class="btn" style="background-color: #f45;">Close</button>
            </div>

            <ul class="filelist" out:slide>
                {#each filenames as file, i}
                    <li out:slide={{delay:(300/filenames.length)*(i+1)}}>
                        <strong>{file}</strong>
                    </li>
                {/each}
            </ul>
        {/if}
        <progress class='{status}' value="{$progress}"  min=0 max=100 title={message}></progress>
    </div>
    <div class="notifier-btn {expand?'expand':'collapse'}" on:click="{()=>expand=!expand}" on:keydown="{()=>true}">{@html misc.arrow}</div>
</div>
