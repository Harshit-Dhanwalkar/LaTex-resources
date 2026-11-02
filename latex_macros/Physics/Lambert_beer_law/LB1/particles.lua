-- particles.lua — Monte Carlo Beer-Lambert

math.randomseed(os.time())

-- Seeded output (for reproducibility)
-- math.randomseed(42)

local cfg = assert(config, "config not set before dofile('particles.lua')")

-- Physics parameters
local cloud_length = cfg.cols * cfg.squareunit
local gamma        = cfg.tau / cloud_length
local n_rays       = 25

-- Draw cloud
local cloud = {}
for i = 1, cfg.cols do
	for j = 1, cfg.rows do
		local r = cfg.rmaxparticle * math.random()
		local l = cfg.squareunit - 2 * r
		local x = (i - 1) * cfg.squareunit + r + l * math.random()
		local y = (j - 1) * cfg.squareunit + r + l * math.random()
		cloud[#cloud + 1] = { x = x, y = y, r = r, hit = false }
	end
end

-- Sample n_rays; each has absorption length L ~ Exp(gamma)
local exit_count = 0
for k = 1, n_rays do
	local y_ray = (k - 0.5) / n_rays * cfg.rows * cfg.squareunit
	local L = -math.log(1 - math.random()) / gamma -- sample from Exp(gamma)
	if L >= cloud_length then
		-- Ray survives to exit
		exit_count = exit_count + 1
		tex.print(
			string.format(
				"\\draw[red!50!white, line width=0.6pt, opacity=0.7] " .. "(0,%.3f)--(%.3f,%.3f);",
				y_ray,
				cloud_length,
				y_ray
			)
		)
	else
		-- Ray absorbed at x = L; find nearest particle and flag it
		local best, bestd = nil, math.huge
		for _, p in ipairs(cloud) do
			-- Lua 5.3 (LuaLaTeX) has no math.hypot
			local dx, dy = p.x - L, p.y - y_ray
			local d = math.sqrt(dx * dx + dy * dy)
			if d < bestd then
				best, bestd = p, d
			end
		end
		if best then
			best.hit = true
		end
		tex.print(
			string.format(
				"\\draw[red!50!white, line width=0.6pt, opacity=0.7] " .. "(0,%.3f)--(%.3f,%.3f);",
				y_ray,
				L,
				y_ray
			)
		)
	end
end

-- Emit Monte Carlo tally
tex.print(
	string.format(
		"\\node[anchor=south west, font=\\footnotesize, text=red!70!black] "
			.. "at (%.2f,%.2f) {MC: $I/I_0 \\approx %.2f$ (%d/%d rays)};",
		-4.5,
		cfg.rows * cfg.squareunit + 0.3,
		exit_count / n_rays,
		exit_count,
		n_rays
	)
)

-- Draw particles, red for those that absorbed a ray
for _, p in ipairs(cloud) do
	local col = p.hit and "red!80!black" or "sand"
	tex.print(string.format("\\fill[%s] (%.3f,%.3f) circle[radius=%.3f];", col, p.x, p.y, p.r))
end
