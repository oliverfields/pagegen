class Plugin():
    def hook_page_pre_build(self, objects):
        '''
   % if len(page.crumb_trail) > 2:
      <ol id="crumb-trail">
        % for p in page.crumb_trail:
          % if not loop.first and not loop.last:
           % if p.relative_url == '/threads/':
              <li><a href="/">${p.title}</a></li>
            % else:
              <li><a href="${p.url_path}">${p.title}</a></li>
            % endif
          % endif
        % endfor
      </ol>
    % endif
        '''

        p = objects['page']
        p.crumb_trail = 'crumb_trail_plugin'
