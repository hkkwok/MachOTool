# This makefile run all (or various sets) of unit tests.

UTILS_TESTS := \
	test_range \
	test_byte_range \
	test_commafy \
	test_mapping

MACH_O_TESTS := \
	test_fat_header \
	test_mach_header \
	test_load_command \
	test_segment_command \
	test_symtab_command \
	test_dysymtab_command 
	

ALL_TESTS := $(UTILS_TESTS) $(MACH_O_TESTS)

all_tests:
	PYTHONPATH=../ python -munittest $(ALL_TESTS)

utils_tests:
	PYTHONPATH=../ python -munittest $(UTILS_TESTS)

mach_o_tests:
	PYTHONPATH=../ python -munittest $(MACH_O_TESTS)
