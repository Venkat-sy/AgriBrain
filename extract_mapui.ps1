$raw = Get-Content 'C:\Users\USER\Downloads\FinalYearProject\req1.txt' -Raw
$idx1 = $raw.IndexOf('### STEP 3:')
$idx2 = $raw.IndexOf('### STEP 4:')
$step3 = $raw.Substring($idx1, $idx2 - $idx1)
$cs = $step3.IndexOf('```tsx')
$ce = $step3.LastIndexOf('```')
$code = $step3.Substring($cs + 6, $ce - $cs - 6)
[IO.File]::WriteAllText('C:\Users\USER\Downloads\FinalYearProject\frontend_web\src\components\MapUI.tsx', $code.Trim())