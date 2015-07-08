#ifndef _SAVEBUFFER_H
#define _SAVEBUFFER_H

#include <png.h>
#include <arv.h>

extern void arv_buffer_save_png(ArvBuffer * buffer, const char * filename);
extern void arv_buffer_save_raw(ArvBuffer * buffer, const char * filename);

#endif //_SAVEBUFFER_H
