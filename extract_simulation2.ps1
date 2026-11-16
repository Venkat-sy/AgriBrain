$raw = Get-Content 'C:\Users\USER\Downloads\FinalYearProject\req1.txt' -Raw
$idx1 = $raw.IndexOf('### STEP 2:')
$idx2 = $raw.IndexOf('### STEP 3:')
$step2 = $raw.Substring($idx1, $idx2 - $idx1)
$cs = $step2.IndexOf('```python')
$ce = $step2.LastIndexOf('```')
$code = $step2.Substring($cs + 9, $ce - $cs - 9)
[IO.File]::WriteAllText('C:\Users\USER\Downloads\FinalYearProject\backend\api\simulation.py', $code.Trim())