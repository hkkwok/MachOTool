TARGET := \
	executable.i386 \
	executable.x86_64 \
	object.o.i386 \
	object.o.x86_64 \

get_arch = $(patsubst $(1).%,%,$(2))

all: $(TARGET)

executable.%: test1.c
	$(CC) -o $@ -arch $(call get_arch,executable,$@) $<

object.o.%: test1.c
	$(CC) -o $@ -arch $(call get_arch,object.o,$@) -c $<

clean:
	rm -f $(TARGET)
