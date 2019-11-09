#include <stdio.h>
#include <string.h>
#include <inttypes.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdbool.h>

void main(int argc, char **argv)
{
    char * bin_filename = "out.bin";
    if(argc >= 2) {
        bin_filename = argv[1];
    }
    FILE* bin_file = fopen(bin_filename,"rb");
    FILE* x_file = fopen("x.csv","w");
    FILE* y_file = fopen("y.csv","w");
    FILE* z_file = fopen("z.csv","w");



    uint16_t sample = 0;
    size_t read_num = fread(&sample, 2, 1, bin_file);

    // while (read_num > 0 && (num_of_samples < 4500*7700))
    while (read_num > 0)
    {
        int sample_type = (sample >> 14);
        //sign extention to 16bits
        if (sample & 0x2000) sample |= 0xC000;
        else sample &= 0x3FFF;

        if(sample_type == 0)
        {
            fprintf(x_file,"%d,", (int16_t)sample);
        }
        else if(sample_type == 1)
        {
            fprintf(y_file,"%d,", (int16_t)sample);
        } 
        else if(sample_type == 2)
        {
            fprintf(z_file,"%d,", (int16_t)sample);
        }
        
        read_num = fread(&sample, 2, 1, bin_file);
    }

    fclose(bin_file);
    fclose(x_file);
    fclose(y_file);
    fclose(z_file);
}
