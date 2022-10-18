import { writable } from "svelte/store";

export const uploadForm = writable(null)
export const newFolderForm = writable(null)
export const showHiddenFiles = writable(localStorage?.getItem('showHiddenFiles')||false)