" Title:        pagegen
" Description:  Helper plugin for working with htpps://pagegen.phnd.net
" Maintainer:   oliverfields

" Prevents the plugin from being loaded multiple times. If the loaded
" variable exists, do nothing more. Otherwise, assign the loaded
" variable and continue running this instance of the plugin.
if exists("g:loaded_pagegen_plugin")
    finish
endif
let g:loaded_pagegen_plugin = 1

" Get threads path from config
let g:plugin_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')
let pagegen_dir = system(g:plugin_dir . '/get_pagegen_dir.sh ' . shellescape(expand('%:p')))[:-2]

if !exists("pagegen_dir")
  finish
endif

let url_map = pagegen_dir . '/url_map.csv'

" Redact
nnoremap <leader>r :execute "normal! ciw" . substitute(expand("<cword>"), '.', '█', 'g')<cr>W
nnoremap <leader>ra :call pagegen#RedactAll(expand("<cword>"))<cr>

" Figure
nnoremap <leader>f :call pagegen#Figure(pagegen_dir)<cr>

" Link
nnoremap <leader>l :call pagegen#PageLink(pagegen_dir)<cr>

" Templates
nnoremap <leader>m :call pagegen#Templates()<cr>

" Tags
nnoremap <leader>t :call pagegen#Tags(pagegen_dir)<cr>
nnoremap <leader>tr :call pagegen#TagsRefresh(pagegen_dir)<cr>

" Open files
nnoremap <leader>o :call pagegen#OpenFile(pagegen_dir, url_map)<cr>
nnoremap <leader>or :call pagegen#OpenMapRefresh(pagegen_dir, url_map)<cr>

" Append
nnoremap <leader>a Go<cr>
