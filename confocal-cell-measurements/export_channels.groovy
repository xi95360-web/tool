// Fiji Script Editor > Language: Groovy > Run. Bio-Formats is supplied by Fiji.
import ij.IJ
import ij.io.DirectoryChooser
import ij.io.OpenDialog
import ij.plugin.ChannelSplitter
import loci.plugins.BF
import loci.plugins.in.ImporterOptions

def source = new OpenDialog("Select microscopy file", null).getPath()
if (source == null) return
def dest = new DirectoryChooser("Select empty export directory").getDirectory()
if (dest == null) return
if (new File(dest).listFiles().length > 0) throw new IllegalArgumentException("Choose an empty export directory")
def options = new ImporterOptions()
options.setId(source)
options.setOpenAllSeries(true)
options.setAutoscale(false)
options.setColorMode(ImporterOptions.COLOR_MODE_GRAYSCALE)
def images = BF.openImagePlus(options)
images.eachWithIndex { image, s ->
    if (image.getNSlices() != 1 || image.getNFrames() != 1) {
        IJ.log("Skipped series ${s}: original Z/T must both equal 1")
    } else {
        def channels = ChannelSplitter.split(image)
        channels.eachWithIndex { channel, c ->
            IJ.saveAsTiff(channel, dest + "series_${s}_channel_${c}.tif")
            channel.close()
        }
        new File(dest + "series_${s}_metadata.txt").text = "source=${source}\noriginal_size_z=1\noriginal_size_t=1\npixel_width=${image.calibration.pixelWidth}\npixel_height=${image.calibration.pixelHeight}\nunit=${image.calibration.unit}\n"
    }
    image.close()
}
IJ.log("Export complete. Verify channel identities and XY units before creating the manifest.")
