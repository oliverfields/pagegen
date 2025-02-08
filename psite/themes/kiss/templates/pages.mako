<%inherit file="base.mako"/>
<%block name="content">
  <%include file="crumb_trail.mako" args="site=site, page=page" />
  ${page.out}
</%block>
