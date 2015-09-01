#include "savebuffer.h"
#include <assert.h>
#include <sys/statvfs.h>

size_t get_free_space()
{
	struct statvfs buf;
	if (statvfs("/", &buf) != 0)
		return 0;
	return buf.f_bsize*buf.f_bfree;
}

/**
 * Reads image data from an Aravis ArvBuffer and saves a png file to filename
 * TODO: Add error checking and all that stuff (this code is demonstrative)
 */
bool arv_buffer_save_png(ArvBuffer * buffer, const char * filename)
{
	fprintf(stderr,"Free space is %d\n", get_free_space());
	if (get_free_space() < 50000000) return false;
	// TODO: This only works on image buffers
	assert(arv_buffer_get_payload_type(buffer) == ARV_BUFFER_PAYLOAD_TYPE_IMAGE);
	
	size_t buffer_size;
	char * buffer_data = (char*)arv_buffer_get_data(buffer, &buffer_size); // raw data
	int width; int height;
	arv_buffer_get_image_region(buffer, NULL, NULL, &width, &height); // get width/height
	int bit_depth = ARV_PIXEL_FORMAT_BIT_PER_PIXEL(arv_buffer_get_image_pixel_format(buffer)); // bit(s) per pixel
	fprintf(stderr, "Bit depth is %d\n", bit_depth);
	//TODO: Deal with non-png compliant pixel formats?
	// EG: ARV_PIXEL_FORMAT_MONO_14 is 14 bits per pixel, so conversion to PNG loses data
	
	int arv_row_stride = width * bit_depth/8; // bytes per row, for constructing row pointers
	int color_type = PNG_COLOR_TYPE_GRAY; //TODO: Check for other types?
	
	// boilerplate libpng stuff without error checking (setjmp? Seriously? How many kittens have to die?)
	png_structp png_ptr = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
	png_infop info_ptr = png_create_info_struct(png_ptr);
	unlink(filename);
	FILE * f = fopen(filename, "wb");
	assert(f != NULL);
	png_init_io(png_ptr, f);
	png_set_IHDR(png_ptr, info_ptr, width, height, bit_depth, color_type,
		PNG_INTERLACE_NONE, PNG_COMPRESSION_TYPE_BASE, PNG_FILTER_TYPE_BASE);
	png_write_info(png_ptr, info_ptr);

	
	// Need to create pointers to each row of pixels for libpng
	png_bytepp rows = (png_bytepp)(png_malloc(png_ptr, height*sizeof(png_bytep)));
	int i =0;
	for (i = 0; i < height; ++i)
		rows[i] = (png_bytep)(buffer_data + (height - i)*arv_row_stride);
	// Actually write image
	png_write_image(png_ptr, rows);
	png_write_end(png_ptr, NULL); // cleanup
	fclose(f);
	return true;
}

bool arv_buffer_save_raw(ArvBuffer * buffer, const char * filename)
{	
	if (get_free_space() < 50000000) return false;
	size_t buffer_size;
	char * buffer_data = (char*)arv_buffer_get_data(buffer, &buffer_size); // raw data
	int width; int height;
	arv_buffer_get_image_region(buffer, NULL, NULL, &width, &height); // get width/height
	int bit_depth = ARV_PIXEL_FORMAT_BIT_PER_PIXEL(arv_buffer_get_image_pixel_format(buffer)); // bit(s) per pixel
	
	FILE * f = fopen(filename, "wb");
	assert(f != NULL);
	fwrite(buffer_data, 1, buffer_size, f);
	fclose(f);		
	return true;
}
