function! pagegen#RedactAll(redact_str)
  if strlen(a:redact_str) > 0
    let censored_str = repeat('█', strlen(a:redact_str))

    execute "%s/" . a:redact_str . "/" . censored_str . "/g"
  endif
endfunction


function! pagegen#Figure(pagegen_dir)
  let search_path = a:pagegen_dir . '/content/assets/media'
  let f = system('find "' . search_path . '" -type f | sed "s#^' . search_path . '/##" | fzy --lines=' . &lines)[:-2]
  redraw!

  if f != ''
    execute 'normal! i<sc>figure("' . f . '", "")</sc>'
    execute 'normal! 6h'
    :startinsert
  endif
endfunction


function! pagegen#OpenMapRefresh(pagegen_dir, url_map)
  let content_dir = a:pagegen_dir . '/content'

  let result = system(g:plugin_dir . '/url_map.sh ' . shellescape(content_dir) . ' ' . shellescape(a:url_map))

  echomsg 'Refreshed ' . a:url_map
endfunction


function! pagegen#OpenFile(pagegen_dir, url_map)
  if !filereadable(a:url_map)
    call pagegen#EditMapRefresh(a:pagegen_dir, a:url_map)
  endif

  let k_save = @k

  " Links will be in markdown link format [text](link), so visual select everything in link paranthesis, assumes cursor is in (link)
  normal! "kyi(

  let selection = @k
  let @k = k_save

  let map_line = system('grep "^' . selection . ';" "' . a:url_map . '"')[:-2]

  if map_line == ''
    echomsg 'No map found for ' . selection
    return
  endif

  let split_map_line = split(map_line, ';')
  let file_path = split_map_line[1]

  if file_path == ''
    echomsg 'No map found for ' . selection
    return
  endif

  let file_path = a:pagegen_dir . '/content/' . file_path

  if filereadable(file_path)
    echomsg "opening " . file_path
    execute 'tabnew ' . fnameescape(file_path)
  else
    echomsg "No file " . file_path
  endif
endfunction


function! pagegen#TagsRefresh(pagegen_dir, tag_file)
  let content_dir = a:pagegen_dir . '/content'
  let result = system('grep -Rih "^tags:" "' . content_dir . '" | sed "s/tags://I ; s/,/\n/g" | sed "s/^[ \t]*// ; s/[ \t]*$//" | sort -u > "' . a:tag_file . '"')
  echomsg 'Refreshed ' . a:tag_file
endfunction


function! pagegen#Tags(pagegen_dir, tag_file)

  if !filereadable(a:tag_file)
    call pagegen#TagsRefresh(a:pagegen_dir, a:tag_file)
  endif

  let t = system('fzy --lines=' . &lines . ' < ' . a:tag_file)[:-2]
  redraw!

  if t != ''
    if getline('.') =~ '^Tags:\ $'
      let prefix = ''
    else
      let prefix = ', '
    endif

    execute 'normal! a' . prefix . t
  endif
endfunction


function! pagegen#PageLink(pagegen_dir)
  let search_path = a:pagegen_dir . '/content'
  let exclude_path = a:pagegen_dir . '*/assets/media*'

  let f = system('find "' . search_path . '" -not -path "' . exclude_path . '" -type f | sed "s#^' . search_path . '/##" | fzy --lines=' . &lines)[:-2]
  redraw!

  if f != ''
    let url = system("python3 -c \"from pagegen.utility_no_deps import urlify; print(urlify('" . f . "'))\"")[:-2]
    let title = system("python3 -c \"from pagegen.utility_no_deps import title_from_path; print(title_from_path('" . f . "'))\"")[:-2]
    execute 'normal! i[' . title . '](/' . url . ')'
    execute "normal! F[l"
    :startinsert
  endif
endfunction


function! pagegen#Templates(template_dir)
  let t = system('[ -d "' . a:template_dir . '" ] && ls -1 "' . a:template_dir . '" | fzy --lines=' . &lines)[:-2]
  redraw!

  if t == ''
    echomsg 'No template selected'
  else
    let template = system(a:template_dir . '/' . t)
    execute "normal! ggdGi" . template
  endif
endfunction


