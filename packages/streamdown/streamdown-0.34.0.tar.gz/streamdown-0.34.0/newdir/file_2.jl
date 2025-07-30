using Plots

function mandelbrot(c, max_iter)
z = c
for n in 1:max_iter
if abs(z) > 2
return n
end
z = z*z + c
end
return max_iter
end

function draw_mandelbrot(xmin, xmax, ymin, ymax, width, height, max_iter)
x = LinRange(xmin, xmax, width)
y = LinRange(ymin, ymax, height)
img = [mandelbrot(complex(r, i), max_iter) for i in y, r in x]
return img
end

img = draw_mandelbrot(-2.0, 1.0, -1.5, 1.5, 1000, 1000, 256)
heatmap(img, aspect_ratio=:equal, legend=false, c=:greys)
savefig("mandelbrot.png")
