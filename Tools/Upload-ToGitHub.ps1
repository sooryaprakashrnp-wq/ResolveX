# Run locally only if you want to upload the prepared project using your own GitHub CLI login.
# Requires Git and GitHub CLI. No credentials are stored by this script.
$ErrorActionPreference='Stop'
$repo='sooryaprakashrnp-wq/ResolveX'
$payload=Split-Path $PSScriptRoot -Parent
function Checked($exe,[string[]]$arguments){ & $exe @arguments; if($LASTEXITCODE -ne 0){throw "$exe command failed"} }
Get-Command git,gh -ErrorAction Stop|Out-Null
Checked gh @('auth','status')
$metadata=& gh repo view $repo --json viewerPermission,isEmpty,defaultBranchRef|ConvertFrom-Json
if($LASTEXITCODE -ne 0){throw 'Cannot inspect repository'}
if($metadata.viewerPermission -notin @('ADMIN','MAINTAIN','WRITE')){throw 'GitHub account lacks repository write access'}
$temp=Join-Path $env:TEMP ('ResolveXUpload-'+[guid]::NewGuid().ToString('N'))
Checked git @('clone',('https://github.com/'+$repo+'.git'),$temp)
Push-Location $temp
try{
 if(Test-Path 'ResolveX_Hackathon'){throw 'ResolveX_Hackathon already exists remotely. Stopped to preserve existing files.'}
 $branch=if($metadata.isEmpty){'main'}else{'resolvex-hackathon-'+(Get-Date -Format 'yyyyMMddHHmmss')}
 if(-not $metadata.isEmpty){Checked git @('checkout','-b',$branch)}
 New-Item 'ResolveX_Hackathon' -ItemType Directory|Out-Null
 # Explicit allowlist prevents uploading local State, approvals, real recipient lists or Output.
 $include=@('project.json','Main.xaml','README.md','.gitignore','Workflows','Docs','Tests','Tools','Data')
 foreach($item in $include){Copy-Item (Join-Path $payload $item) 'ResolveX_Hackathon/' -Recurse}
 New-Item 'ResolveX_Hackathon/Config' -ItemType Directory|Out-Null
 foreach($item in @('AI-response.schema.json','SendApproval.example.json')){Copy-Item (Join-Path $payload ('Config/'+$item)) 'ResolveX_Hackathon/Config/'}
 Set-Content 'ResolveX_Hackathon/Config/AI.json' '{"Endpoint":"","ApiKeyEnvironmentVariable":"RESOLVEX_AI_KEY","ConfidenceThreshold":0.75}' -Encoding UTF8
 Set-Content 'ResolveX_Hackathon/Config/AuthorizedRecipients.json' '[]' -Encoding UTF8
 Set-Content 'ResolveX_Hackathon/Config/ManualReviewRecipients.json' '[]' -Encoding UTF8
 # Refuse upload if demo routing addresses were replaced with live addresses.
 # Portable static verifier validates all blank routes and shipped disabled configuration.
 $python=Get-Command python -ErrorAction SilentlyContinue
 if(-not $python){throw 'Python required for this upload-only preflight; normal UiPath execution does not require Python.'}
 Checked python @('ResolveX_Hackathon/Tests/verify_static.py')
 Checked git @('add','ResolveX_Hackathon')
 Checked git @('add','-f','ResolveX_Hackathon/Config/AuthorizedRecipients.json','ResolveX_Hackathon/Config/ManualReviewRecipients.json')
 Checked git @('commit','-m','Add ResolveX multi-organization complaint prototype core and tests')
 Checked git @('push','origin',('HEAD:refs/heads/'+$branch))
 if(-not $metadata.isEmpty){
  Checked gh @('pr','create','--draft','--repo',$repo,'--head',$branch,'--base',$metadata.defaultBranchRef.name,'--title','Add ResolveX hackathon prototype core','--body','Adds modular UiPath workflows, five Excel files, sample fixtures and validation instructions. Native Gmail adapters require binding to the existing authorized connection. Sending fails closed by default. Existing repository files are preserved.')
 }
 Write-Host ('Uploaded branch: https://github.com/'+$repo+'/tree/'+$branch+'/ResolveX_Hackathon')
}finally{Pop-Location}
# Clone retained for review and troubleshooting.
Write-Host ('Local review clone: '+$temp)
