require 'chunky_png'

class Mandelbrot
def initialize(xmin, xmax, ymin, ymax, width, height, max_iter)
@xmin, @xmax, @ymin, @ymax = xmin, xmax, ymin, ymax
@width, @height, @max_iter = width, height, max_iter
end

def mandelbrot(c)
z = c
(0...@max_iter).each do |n|
return n if z.abs > 2
z = z * z + c
end
@max_iter
end

def draw
pixels = Array.new(@height) { Array.new(@width, 0) }
(0...@height).each do |y|
(0...@width).each do |x|
c = Complex((x.to_f / @width) * (@xmax - @xmin) + @xmin, (y.to_f / @height) * (@ymax - @ymin) + @ymin)
pixels[y][x] = mandelbrot(c)
end
end
pixels
end

def save(filename)
pixels = draw
png = ChunkyPNG::Image.new(@width, @height, ChunkyPNG::Color::TRANSPARENT)
(0...@height).each do |y|
(0...@width).each do |x|
color = (pixels[y][x].to_f / @max_iter * 255).to_i
png[x, y] = ChunkyPNG::Color.rgb(color, color, color)
end
end
png.save(filename)
end
end

mandelbrot = Mandelbrot.new(-2.0, 1.0, -1.5, 1.5, 1000, 1000, 256)
mandelbrot.save('mandelbrot.png')
