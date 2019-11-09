#include <stdio.h>
#include <string.h>
#include <inttypes.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdbool.h>

#define ADC_SAMPLING_TIME_US (13)
#define SAMPLES_PER_AVERAGE (10)
#define AVERAGE_TIME_US (SAMPLES_PER_AVERAGE * ADC_SAMPLING_TIME_US)

typedef union {
    float val;
    unsigned char bytes[4];
} Float_t;

typedef union {
    uint32_t val;
    unsigned char bytes[4];
} Uint32_t;

void main(int argc, char **argv)
{
    char * bin_filename = "out.bin";
    char * csv_filename = "out.csv";
    if(argc >= 2) {
        bin_filename = argv[1];
    }
    if(argc >= 3) {
        csv_filename = argv[2];
    }
    FILE* bin_file = fopen(bin_filename,"rb");
    FILE* out_file = fopen(csv_filename,"w");

    unsigned char byte = 0;
    unsigned char payload[5];
    int pos = 0;
    bool esc_flag = false;
    size_t read_num = fread(&byte, 1, 1, bin_file);
    uint64_t timestamp = 0;
    uint32_t num_of_samples = 0;
    // while (read_num > 0 && (num_of_samples < 4500*7700))
    while (read_num > 0)
    {
        // printf("%d, %x\n",pos, byte);
        if(esc_flag)
        {
            payload[pos++] = (byte ^ 0x20);
            esc_flag = false;
        }
        else
        {
            switch(byte)
            {
                case 3:
                    if(pos == 4)
                    {
                        Float_t reading;
                        memcpy(reading.bytes, payload, 4);
                        // if(num_of_samples > (8500*7700))
                            fprintf(out_file,"%f,", reading.val);   
                        num_of_samples++;
                        // fprintf(out_file,"%ld,\n", timestamp);
                        timestamp += AVERAGE_TIME_US;
                    }
                    else if(pos == 5)
                    {
                        Uint32_t reading;
                        memcpy(reading.bytes, payload, 4);
                        uint64_t new_ts = reading.val;
                        new_ts += ADC_SAMPLING_TIME_US;
                        if(timestamp + AVERAGE_TIME_US < new_ts)
                        {
                            printf("missing timestamps!!! old ts = %" PRId64 " new_ts = %" PRId64 "\n", timestamp, new_ts);
                        }
                        else
                        {
                            printf("receevied good timestamp :)))))");
                        }
                        timestamp = new_ts;
                    }
                    else
                    {
                        printf("!!!!! payload too long (pos = %d)\n",pos);
                    }
                    pos = 0;
                break;

                case 31:
                    esc_flag = true;
                break;

                default:
                payload[pos++] = byte;
                break;
            }
        }
        read_num = fread(&byte, 1, 1, bin_file);
    }
    printf("num_of_samples = %d\n", num_of_samples);
    // fseeko(out_file,-1,SEEK_END);
    // int position = ftello(out_file);
    // ftruncate(fileno(out_file), position);

    fclose(bin_file);
    fclose(out_file);
}
