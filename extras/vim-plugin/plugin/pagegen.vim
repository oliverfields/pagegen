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
let pagegen_vim_dir = pagegen_dir . '/vim'
let pagegen_var_dir = pagegen_vim_dir . '/var'
let pagegen_vimrc = pagegen_vim_dir . '/pagegen.vim'
let pagegen_template_dir = pagegen_vim_dir . '/templates'
let url_map = pagegen_var_dir . '/url_map.csv'
let tag_file = pagegen_var_dir . '/tags'
let vim_scripts_file = pagegen_vim_dir . '/vim-scripts'

if isdirectory(g:pagegen_dir)
  if !isdirectory(g:pagegen_var_dir)
    call mkdir(g:pagegen_var_dir, "p")
  endif
endif

" Source local vimrc if exists
if filereadable(pagegen_vimrc)
  execute 'source ' . pagegen_vimrc
endif

" Figure
nnoremap <leader>f :call pagegen#Figure(pagegen_dir)<cr>

" Link
nnoremap <leader>l :call pagegen#PageLink(pagegen_dir)<cr>

" Templates
nnoremap <leader>m :call pagegen#Templates(pagegen_template_dir)<cr>

" Tags
nnoremap <leader>t :call pagegen#Tags(pagegen_dir, tag_file)<cr>
nnoremap <leader>tr :call pagegen#TagsRefresh(pagegen_dir, tag_file)<cr>

" Suggest tags/keywords
nnoremap <leader>k :call pagegen#SuggestKeywords(pagegen_dir)<cr>

" Open url file
nnoremap <leader>o :call pagegen#OpenFile(pagegen_dir, url_map)<cr>
nnoremap <leader>or :call pagegen#OpenMapRefresh(pagegen_dir, url_map)<cr>

