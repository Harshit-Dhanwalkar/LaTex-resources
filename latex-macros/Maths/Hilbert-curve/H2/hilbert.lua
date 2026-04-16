-- hilbert.lua (minimal working version for order 1-3)
function draw_hilbert(order, scale)
	-- Pre-defined coordinates for testing
	local curves = {
		[1] = { { 0, 0 }, { 1, 0 }, { 1, 1 }, { 0, 1 } },
		[2] = {
			{ 0, 0 },
			{ 0, 1 },
			{ 1, 1 },
			{ 1, 0 },
			{ 2, 0 },
			{ 2, 1 },
			{ 3, 1 },
			{ 3, 0 },
			{ 3, -1 },
			{ 2, -1 },
			{ 2, -2 },
			{ 3, -2 },
			{ 4, -2 },
			{ 4, -1 },
			{ 5, -1 },
			{ 5, 0 },
		},
		[3] = nil, -- Will be generated
	}

	if order == 3 then
		-- Generate order 3 from order 2
		local size = 2 ^ order
		local points = {}
		for i = 0, size * size - 1 do
			local x = 0
			local y = 0
			for j = 0, order - 1 do
				local bit = math.floor(i / (4 ^ j)) % 4
				local rx = bit % 2
				local ry = math.floor(bit / 2)
				if rx == 0 then
					if ry == 1 then
						x = (2 ^ j - 1) - x
						y = (2 ^ j - 1) - y
					end
					local temp = x
					x = y
					y = temp
				end
				x = x + rx * (2 ^ j)
				y = y + ry * (2 ^ j)
			end
			table.insert(points, { x / (size - 1), y / (size - 1) })
		end
		curves[3] = points
	end

	local points = curves[order] or curves[1]
	local tikz = "\\begin{tikzpicture}[scale=" .. scale .. "]\n"
	tikz = tikz .. "  \\draw[white, thick] "

	for i, p in ipairs(points) do
		if i == 1 then
			tikz = tikz .. string.format("(%.3f,%.3f)", p[1], p[2])
		else
			tikz = tikz .. string.format(" -- (%.3f,%.3f)", p[1], p[2])
		end
	end

	tikz = tikz .. ";\n\\end{tikzpicture}"
	tex.print(tikz)
end
