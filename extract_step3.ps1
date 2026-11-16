$content = Get-Content 'C:\Users\USER\Downloads\FinalYearProject\req1.txt' -Raw
$idx = $content.IndexOf('### STEP 3:')
$step3 = $content.Substring($idx)
$idx2 = $step3.IndexOf('### STEP 4:')
$step3 = $step3.Substring(0, $idx2)
$cs = $step3.IndexOf('```tsx')
$ce = $step3.LastIndexOf('```')
$code = $step3.Substring($cs + 6, $ce - $cs - 6)
[IO.File]::WriteAllText('C:\Users\USER\Downloads\FinalYearProject\frontend_web\src\components\MapUI.tsx', $code.Trim())