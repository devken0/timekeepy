on run argv
	set repoDir to item 1 of argv
	try
		set userChoice to button returned of (display dialog ¬
			"Time to time in for your shift?" ¬
			buttons {"Ignore", "Time in now"} ¬
			default button "Time in now" ¬
			with title "Timekeepy" ¬
			with icon note)
		if userChoice is "Time in now" then
			do shell script "open " & quoted form of (repoDir & "/run.command")
		end if
	on error errMsg number errNum
		if errNum is not -128 then error errMsg number errNum
	end try
end run
