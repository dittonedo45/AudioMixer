#include <iostream>
#include <vector>
extern "C" {
#include <libavformat/avformat.h>
#include <libavcodec/avcodec.h>
#include <libavfilter/avfilter.h>
};

using std::string;
using std::exception;
using std::vector;

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

struct a_ins_mem : public exception {
	string wh;
	a_ins_mem (string g) : wh (g) {}
	const char* what ()
	{
		return wh.data();
	}
};

struct a_exception : public exception {
	virtual const char*what ()
	{
		return "Audio::Error: <main>";
	}
};

struct a_find_stream_error : public a_exception {
	virtual const char*what ()
	{
		return "Audio::Error: <a_find_stream_error>";
	}
};

struct Codec {
	int ret, stream_index;
	AVCodecContext* dec_ctx{NULL};
	AVCodec *d{NULL};

	operator AVCodec**(){
		return &d;
	}

	Codec (){}

	Codec(const Codec& c)
	{
		ret=c.ret;
		stream_index=c.stream_index;
		d=c.d;
		dec_ctx=c.dec_ctx;
	}

	void alloc()
	{
		dec_ctx = avcodec_alloc_context3 (d);
		if (dec_ctx==NULL)
		{
			throw a_ins_mem ("Failed to allocate Codec:");
		}
	}

	~Codec ()
	{
		using namespace std;
		cerr<<"Codec closed."<<endl;
		avcodec_free_context (&dec_ctx);
	}
};

struct Format {
	AVFormatContext* fmtctx{NULL};
	int ret, stream_index;
	Codec ctx;

	operator int()
	{
		return stream_index;
	}
	operator AVFormatContext*()
	{
		return fmtctx;
	}
	Format (const Format& f)
	{
		fmtctx=f.fmtctx;
		ret=f.ret;
		stream_index=f.stream_index;
		ctx=f.ctx;
	}

	Format (char *str)
	{
		ret=avformat_open_input (&fmtctx,
				str, NULL, NULL);
		if (ret<0) {
			throw a_exception ();
		}
		stream_index=ret=av_find_best_stream (fmtctx, AVMEDIA_TYPE_AUDIO,
				-1, -1, ctx, NULL);
		try{
		ctx.alloc ();
		} catch (a_ins_mem& exp)
		{
			using std::cerr;
			using std::endl;

			cerr<<exp.what()<<endl;
			throw;
		}
	}

	void find_stream ()
	{
		ret=avformat_find_stream_info (fmtctx, NULL);
		if (ret<0) {
			throw a_find_stream_error ();
		}
	}

	~Format ()
	{
		using namespace std;
		cerr<<"Format:: closed."<<endl;
		avformat_free_context(fmtctx);
	}

};


auto main(int argsc, char **args) -> int
{
	if (argsc<2) abort();
	vector<Format*> f;
	for (char **p=&args[1]; p && *p; p++)
	{
		f.push_back (new Format(*p));
	}
	for(Format*& t: f)
	{
		delete t;
	}
	return int(0);
}
