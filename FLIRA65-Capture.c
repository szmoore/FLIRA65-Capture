// Aravis capture program.

#define _POSIX_C_SOURCE 200809L

#include <aravis-0.4/arv.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include "savebuffer.h"

static gboolean cancel = FALSE;

static void
set_cancel (int signal)
{
	cancel = TRUE;
}

static char *arv_option_camera_name = "FLIR Systems AB-62600164";
static char *arv_option_debug_domains = NULL;
static gboolean arv_option_auto_buffer = FALSE;
static int arv_option_width = -1;
static int arv_option_height = -1;
static int arv_option_horizontal_binning = -1;
static int arv_option_vertical_binning = -1;
static int arv_option_max_frames = 1;
static int arv_option_max_errors_before_abort = 10;
static char * arv_option_save_dir = ".";
static char * arv_option_save_prefix = "";
static char * arv_option_save_type = "png";
static int arv_option_pixel_format = 8;
static int arv_option_sample_period = 0;

typedef bool(*SaveBuffer)(ArvBuffer*, const char*);
static SaveBuffer save_buffer_fn = NULL;

static SaveBuffer GetSaveBufferFn(const char * type)
{
	if (strcmp(type, "png") == 0)
		return arv_buffer_save_png;
	if (strcmp(type, "raw") == 0)
		return arv_buffer_save_raw;
	return NULL;
}

static const GOptionEntry arv_option_entries[] =
{
	{ "name",		'n', 0, G_OPTION_ARG_STRING,
		&arv_option_camera_name,"Camera name", NULL},
	{ "auto",		'a', 0, G_OPTION_ARG_NONE,
		&arv_option_auto_buffer,	"AutoBufferSize", NULL},
	{ "width", 		'w', 0, G_OPTION_ARG_INT,
		&arv_option_width,		"Width", NULL },
	{ "height", 		'h', 0, G_OPTION_ARG_INT,
		&arv_option_height, 		"Height", NULL },
	{ "h-binning", 		'\0', 0, G_OPTION_ARG_INT,
		&arv_option_horizontal_binning,"Horizontal binning", NULL },
	{ "v-binning", 		'\0', 0, G_OPTION_ARG_INT,
		&arv_option_vertical_binning, 	"Vertical binning", NULL },
	{ "debug", 		'd', 0, G_OPTION_ARG_STRING,
		&arv_option_debug_domains, 	"Debug mode", NULL },
	{ "frames",	'f',0, G_OPTION_ARG_INT, &arv_option_max_frames, "Number of frames to save", NULL},
	{ "directory", 'D', 0, G_OPTION_ARG_STRING, &arv_option_save_dir, "Directory for frame files (defaults to .)", NULL},
	{ "prefix", 'p',0, G_OPTION_ARG_STRING, &arv_option_save_prefix, "Prefix for frame files (defaults to Timestamp)", NULL},
	{ "type", 't',0, G_OPTION_ARG_STRING, &arv_option_save_type, "Type of file to save frames as", NULL},
	{ "errors", 'e', 0, G_OPTION_ARG_INT, &arv_option_max_errors_before_abort, "Errors before aborting", NULL},
	{ "pixel-format", 'F', 0, G_OPTION_ARG_INT, &arv_option_pixel_format, "Pixel format", NULL},
	{ "sample-period", 'T', 0, G_OPTION_ARG_INT, &arv_option_sample_period, "Sample period", NULL},
	{ NULL }
};

int main (int argc, char **argv)
{
	
	ArvCamera * camera;
	ArvStream *stream;
	ArvBuffer *buffer;
	GOptionContext *context;
	GError *error = NULL;
	char memory_buffer[100000];
	int i;

	arv_g_thread_init (NULL);
	arv_g_type_init ();

	context = g_option_context_new (NULL);
	g_option_context_add_main_entries (context, arv_option_entries, NULL);

	if (!g_option_context_parse (context, &argc, &argv, &error)) {
		g_option_context_free (context);
		g_print ("Option parsing failed: %s\n", error->message);
		g_error_free (error);
		return EXIT_FAILURE;
	}

	g_option_context_free (context);
	if (arv_option_max_frames < 0)
		arv_option_max_errors_before_abort = -1;
	
	save_buffer_fn = GetSaveBufferFn(arv_option_save_type);

	arv_debug_enable (arv_option_debug_domains);

	if (arv_option_camera_name == NULL)
		g_print ("Looking for the first available camera\n");
	else
		g_print ("Looking for camera '%s'\n", arv_option_camera_name);

	camera = arv_camera_new (arv_option_camera_name);
	
	int errors = 0;
	if (camera == NULL)
	{
		g_print("No device found");
		return 1;
	}

	guint payload_size = arv_camera_get_payload(camera);
	g_print ("payload size  = %d (0x%x)\n", payload_size, payload_size);
	

	stream = arv_camera_create_stream (camera, NULL, NULL);
	if (arv_option_auto_buffer)
	{
		g_object_set (stream,"socket-buffer", ARV_GV_STREAM_SOCKET_BUFFER_AUTO,"socket-buffer-size", 0,NULL);
	}
	
	for (i = 0; i < 30; i++)
	{
		arv_stream_push_buffer (stream, arv_buffer_new (payload_size, NULL));
	}
	
	arv_camera_stop_acquisition(camera);

	// set the bit depth
	ArvDevice * device = arv_camera_get_device(camera);
	ArvGcNode * feature = arv_device_get_feature(device, "PixelFormat");
	char * pix_format = "Mono8";
	if (arv_option_pixel_format == 14)
		pix_format = "Mono14";
	arv_gc_feature_node_set_value_from_string(ARV_GC_FEATURE_NODE(feature), pix_format, NULL);
	if (arv_option_pixel_format == 14)
	{
		feature = arv_device_get_feature(device, "CMOSBitDepth");
		arv_gc_feature_node_set_value_from_string(ARV_GC_FEATURE_NODE(feature), "bit14bit", NULL);
	}


	signal (SIGINT, set_cancel);
	signal (SIGQUIT, set_cancel);

	int captured_frames = 0;
	guint64 timeout=1000000;
	#define _CAN_STOP (arv_option_max_frames > 0 && captured_frames >= arv_option_max_frames)
	arv_camera_start_acquisition(camera);
	do {
		g_usleep (100000);
			do  {
			buffer = arv_stream_timeout_pop_buffer (stream, timeout);
			if (buffer == NULL) break;
			ArvBufferStatus status = arv_buffer_get_status(buffer);
			fprintf(stderr, "Status is %d\n", status);
			if (status == ARV_BUFFER_STATUS_SUCCESS)
			{
		
				
				
				if (timeout > 100000) timeout -= 1000;
				errors = 0;
				if (save_buffer_fn != NULL)
				{
					struct timespec timestamp;
					clock_gettime(CLOCK_REALTIME, &timestamp);
					char filename[BUFSIZ];
					if (strcmp(arv_option_save_prefix,"") != 0)
					{
						sprintf(filename, "%s/%s%d.%s", arv_option_save_dir,arv_option_save_prefix, captured_frames, arv_option_save_type);
					}
					else
					{
						sprintf(filename, "%s/%d.%03ld.%s", arv_option_save_dir, (int)timestamp.tv_sec, (long)(timestamp.tv_nsec/1.0e6), arv_option_save_type);
					}
					if ((*save_buffer_fn)(buffer, filename) == false)
					{
						g_print("Couldn't save frame %d to %s\n", captured_frames, filename);
						set_cancel(SIGQUIT);
					}
					g_print("Saved frame %d to %s\n", captured_frames, filename);
					char latest[] = "latest.png";
					sprintf(latest, "latest.%s", arv_option_save_type);
					unlink(latest);
					symlink(filename, latest);
				}
				captured_frames++;
				g_usleep(arv_option_sample_period);
			}
			else 
			{
				if (timeout < 10000000) timeout+=1000;
				fprintf(stderr, "%d errors out of %d allowed\n", errors, arv_option_max_errors_before_abort);
				arv_camera_stop_acquisition(camera);
				if (++errors > arv_option_max_errors_before_abort && arv_option_max_errors_before_abort >= 0)
				{
					set_cancel(SIGQUIT);
				}
				else
				{
					arv_camera_start_acquisition(camera);
				}
			}
			arv_stream_push_buffer (stream, buffer);
			
			
			
		} while (!cancel && buffer != NULL && !_CAN_STOP);
	} while (!cancel && !_CAN_STOP);
	arv_camera_stop_acquisition(camera);


	guint64 n_processed_buffers; guint64 n_failures; guint64 n_underruns;
	arv_stream_get_statistics (stream, &n_processed_buffers, &n_failures, &n_underruns);
	g_print ("Processed buffers = %Lu\n", (unsigned long long) n_processed_buffers);
	g_print ("Failures          = %Lu\n", (unsigned long long) n_failures);
	g_print ("Underruns         = %Lu\n", (unsigned long long) n_underruns);


	g_object_unref (stream);
	g_object_unref (camera);
	
	
	return (errors > 0);
}
