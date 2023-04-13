#include <iostream>
#include <vector>
#include <memory>
extern "C" {
#include <libavformat/avformat.h>
#include <python3.8/Python.h>
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
		if (dec_ctx)
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
	Format () {}

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
		avformat_free_context(fmtctx);
	}

};

struct fobject {
	PyObject_HEAD
	Format* fmtctx;
};
namespace f
{
	using T=PyObject*;
	T fobject_new (PyTypeObject* t, T a, T k)
	{
		return t->tp_alloc(t, 0);
	}
	int fobject_init (T t, T a, T k)
	{
		fobject* fb=(fobject*)t;
		char *path;

		if (!PyArg_ParseTuple (a, "s", &path))
			return 1;
		try{
			fb->fmtctx=new Format(path);
		}catch(a_exception& exp)
		{
			PyErr_Format (PyExc_RuntimeError,
				exp.what ());
			return 1;
		}catch(...){
			PyErr_Format (PyExc_RuntimeError,
				"Failed to allocate.");
			return 1;
		}
		return 0;
	}
	void fobject_dealloc (T o)
	{
		fobject* f=(fobject*) o;
		delete f->fmtctx;
	}
	static PyTypeObject fobject_type ={
		PyVarObject_HEAD_INIT (NULL, 0)
		.tp_name="AVFormatContext",
		.tp_init=fobject_init,
		.tp_dealloc=fobject_dealloc,
		.tp_new=fobject_new,
		.tp_basicsize=sizeof(fobject),
		.tp_flags=Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE
	};

	PyMODINIT_FUNC
	PyInit_av ()
	{
		static struct PyModuleDef avv={
			PyModuleDef_HEAD_INIT,
			"audio_video",
			0, -1, NULL
		};

		PyObject *ov=PyModule_Create (&avv);
		PyType_Ready (&fobject_type);

		PyModule_AddObject (ov, "Format",
				(T)&fobject_type);

		return ov;
	}
}

auto main(int argsc, char **args) -> int
{
	using namespace std;
	PyImport_AppendInittab ("fobject", &f::PyInit_av);
	Py_InitializeEx (0);
	Py_BytesMain (argsc, args);
	Py_Finalize ();
	return int(0);
}
