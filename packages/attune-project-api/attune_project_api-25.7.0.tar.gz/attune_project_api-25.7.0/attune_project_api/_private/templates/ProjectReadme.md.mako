<%page args="makoGlobal, projectMetadata, params, niceParameterNames, files,
                blueprints"/>
<%
    domain = "attuneops.io"
    shields = "https://img.shields.io"
    logo = f"https://{domain}/wp-content/uploads/2020/10/cropped-server_tribe_favicon.png"
    docsBadge = f"{shields}/badge/docs-latest-brightgreen.svg"
    docsLink = f"http://docs.{domain}"
    chatBadge = f"{shields}/discord/844971127703994369"
    chatLink = f"http://discord.{domain}"
    videosBadge = f"{shields}/badge/videos-watch-brightgreen.svg"
    videosLink = f"https://www.youtube.com/@attuneops"
    downloadBadge = f"{shields}/badge/download-latest-brightgreen.svg"
    downloadLink = f"https://download.{domain}/"
%>
<p align="center">
    <a href="${docsLink}">
        <img src="${docsBadge}" /></a>
    <a href="${chatLink}">
        <img src="${chatBadge}" /></a>
    <a href="${videosLink}">
        <img src="${videosBadge}" /></a>
    <a href="${downloadLink}">
        <img src="${downloadBadge}" /></a>
</p>
<p align="center">
  <a href="https://attuneops.io/" target="_blank">
    <img src="${logo}" alt="Attune for Digital Ops"  width="100" height="100" />
  </a>
</p>

# ${projectMetadata.name}

${projectMetadata.makeCommentMarkdown(topHeaderNum=2)}

<%include file="ProjectReadmeAttune.md.mako" args=""/>
<%include file="ProjectReadmeCloneInstructions.md.mako" args=""/>
<%include file="ProjectReadmeBlueprints.md.mako" args="blueprints=blueprints"/>
<%include file="ProjectReadmeContribute.md.mako" args=""/>

---

**Thank you**
