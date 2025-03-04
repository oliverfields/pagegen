function! pagegen#Figure(pagegen_dir)
  let search_path = a:pagegen_dir . '/assets'
  let f = system('find "' . search_path . '" -type f | sed "s#^' . search_path . '/##" | fzy "--prompt=Media > " --lines=' . &lines)[:-2]
  redraw!

  if f != ''
    execute 'normal! i<sc>figure("' . f . '", "")</sc>'
    execute 'normal! 6h'
    :startinsert
  endif
endfunction


function! pagegen#SuggestKeywords(pagegen_dir)
  let f=join(getline(1, '$'), "\n")
  let result = system(g:plugin_dir . '/suggest_keywords.sh ' . shellescape(a:pagegen_dir . '/stopwords.txt'), f)[:-2]

  if result == ''
    echomsg 'No keywords found that have sufficient frequency'
  else
    let tags_line = 'Tags: '
    " Subtrackt 1 because using this for array index value later
    let tags_line_len = len(tags_line) - 1
    :normal! gg<cr>
    call search('^' . tags_line)

    let l = getline('.')

    if l == tags_line
      execute ':normal! A' . result
    else
      " If line starts with tagsLine
      echomsg l[0:tags_line_len]
      if l[0:tags_line_len] == tags_line
        execute ':normal! A, ' . result
      else
        execute ':normal! O' . tags_line . result
      endif
    endif
  endif
endfunction


function! pagegen#OpenMapRefresh(pagegen_dir, url_map)
  let content_dir = a:pagegen_dir . '/content'

  let result = system(g:plugin_dir . '/url_map.sh ' . shellescape(content_dir) . ' ' . shellescape(a:url_map))

  echomsg 'Refreshed ' . a:url_map
endfunction


function! pagegen#OpenFile(pagegen_dir, url_map)
  if !filereadable(a:url_map)
    call pagegen#OpenMapRefresh(a:pagegen_dir, a:url_map)
  endif

  let k_save = @k

  " Links will be in markdown link format [text](link) or part of figure shortcode figure("link", "text"), so visual select everything in () first
  normal! "kyi(

  let selection = @k

  let @k = k_save

  " If selection is figure then try to open media
  if selection[0] == '"'
    let selection = a:pagegen_dir . '/content/assets/' . substitute(@k[1:], '".*', '', 'g')
    silent execute '!xdg-open "' . selection . '"'
    return
  endif

  " Selection is a page, so convert url to file path and then open in vim
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
    echomsg "Opening " . file_path
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

  let t = system('fzy "--prompt=Tags > " --lines=' . &lines . ' < ' . a:tag_file)[:-2]
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

  let f = system('find "' . search_path . '" -type f | sed "s#^' . search_path . '/##" | fzy "--prompt=Pages > " --lines=' . &lines)[:-2]
  redraw!

  if f != ''
    let url = f
    let title = pagegen#TitleifyFilename(f)

    execute 'normal! i[' . title . '](/' . url . ')'
    execute "normal! F[l"
    :startinsert
  endif
endfunction


function! pagegen#TitleifyFilename(name)

    let title = substitute(a:name, ".*/", "", "g")

    if title == 'index'
        let title = expand("%:p:h:t")
    endif

    let title = substitute(title, "-", " ", "g")
    let title = substitute(title, ".", "\\U\\0", "")

    return title
endfunction


function! pagegen#Templates(template_dir)
  let t = system('[ -d "' . a:template_dir . '" ] && ls -1 "' . a:template_dir . '" | fzy "--prompt=Templates > " --lines=' . &lines)[:-2]
  redraw!

  echomsg a:template_dir

  if t == ''
    echomsg 'No template selected'
  else
    let title = pagegen#TitleifyFilename(expand("%:t"))
    " execute template and pass titleified file name as argument
    let template = system(a:template_dir . '/' . t . ' "' . title . '"')
    execute "normal! ggdGi" . template
  endif
endfunction

