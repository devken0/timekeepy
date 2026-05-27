try
	set userChoice to button returned of (display dialog ¬
		"Have you already timed out for today?" ¬
		buttons {"Ignore", "Time out now"} ¬
		default button "Time out now" ¬
		with title "Timekeepy" ¬
		with icon caution)
	if userChoice is "Time out now" then
		do shell script "open /Users/ken/Code/timekeepy/run.command"
	end if
on error errMsg number errNum
	if errNum is not -128 then error errMsg number errNum
end try
