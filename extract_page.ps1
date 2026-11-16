$raw = Get-Content 'C:\Users\USER\Downloads\FinalYearProject\req1.txt' -Raw
$idx1 = $raw.IndexOf('### STEP 4:')
$idx2 = $raw.IndexOf('### STEP 5:')
$step4 = $raw.Substring($idx1, $idx2 - $idx1)
$cs = $step4.IndexOf('```tsx')
$ce = $step4.LastIndexOf('```')
$code = $step4.Substring($cs + 6, $ce - $cs - 6)
[IO.File]::WriteAllText('C:\Users\USER\Downloads\FinalYearProject\frontend_web\src\app\simulate\page.tsx', $code.Trim())