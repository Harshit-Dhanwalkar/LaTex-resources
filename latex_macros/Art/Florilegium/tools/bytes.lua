-- Measure content-stream bytes of each primitive, without TeX:
--   texlua tools/bytes.lua          (from the repo root; or: tools/in-docker texlua tools/bytes.lua)
tex = { sprint = function() end }
luatexbase = {
	registernumber = function()
		return 0
	end,
}
local written = 0
node = {
	new = function()
		return {}
	end,
	write = function(n)
		written = written + #n.data
	end,
}
package.path = "./?.lua;" .. package.path
local ink, flora = require("ink"), require("flora")
local function measure(name, fn)
	local tot = 0
	for k = 1, 10 do
		ink.set_transform({ ink.CM, 0, 0, ink.CM, 0, 0 })
		written = 0
		fn(ink.rng(k))
		ink.flush()
		tot = tot + written
	end
	print(string.format("%-12s %7.1f KB", name, tot / 10 / 1024))
end
measure("flower 1.2", function(r)
	flora.flower(r, 1.2)
end)
measure("petal 1.2", function(r)
	ink.scale(1.2)
	flora.petal(r)
end)
measure("lily 1.1", function(r)
	flora.lily(r, 1.1)
end)
measure("blossom .3", function(r)
	flora.blossom(r, 0.3)
end)
measure("leaf 2.0", function(r)
	ink.scale(2)
	flora.leaf(r, { depth = 0.6 })
end)
measure("leaf ent 2", function(r)
	ink.scale(2)
	flora.leaf(r, { depth = 0 })
end)
measure("leaflet .6", function(r)
	ink.scale(0.6)
	flora.leaflet(r)
end)
measure("cyme 2", function(r)
	flora.cyme(r, 2)
end)
measure("sprig 2", function(r)
	flora.sprig(r, 2)
end)
measure("umbel 1.2", function(r)
	flora.umbel(r, 1.2)
end)
measure("floret .1", function(r)
	flora.floret(r, 0.1)
end)
measure("bud .6", function(r)
	flora.bud(r, 0.6)
end)
measure("stem 20cm", function(r)
	local p = {}
	for i = 0, 80 do
		p[#p + 1] = { math.sin(i / 9), i / 4 }
	end
	flora.stem(p, 0.08, 0.03)
end)
