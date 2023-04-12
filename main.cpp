#include <iostream>
extern "C" {
#include <libavformat/avformat.h>
#include <libavcodec/avcodec.h>
#include <libavfilter/avfilter.h>
};

using std::string;
struct b_string : public string 
{
	b_string (char* s) : string(s){}

	operator const char*()
	{
		return data();
	}
	operator char*()
	{
		return (char*)data();
	}
};

void transcode_ (char *str)
{
	AVFormatContext* fmtctx{NULL};
	AVCodecContext
	int ret;

	ret=avformat_open_input (&fmtctx,
			str, NULL, NULL);
	if (ret<0) {
		abort ();
	}
	ret=avformat_find_stream_info (fmtctx, NULL);
	if (ret<0) {
		abort ();
	}

	avformat_free_context(fmtctx);
}

auto main(int argsc, char **args) -> int
{
	if (argsc<2) abort();

	b_string s(args[1]);
	transcode_ (s);
	return int(0);
}
