#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef struct packet
{
    int id;
    int src;
    int dest;
    float size;
    float timstamp;
} packet;

typedef struct packets
{
    packet *pks;
    int num;
} packets;

packets parse_workload(char *path);
packet packet_from_line(char *line);
void free_packets(packets *pks);

int main()
{
    char *path = "workloads/trace_second_SG.txt";
    packets pks = parse_workload(path);

    for (int i = 0; i < 100; i++)
    {
        printf("packet: %d, %d, %d, %f, %f \n", pks.pks[i].id, pks.pks[i].src, pks.pks[i].dest, pks.pks[i].size, pks.pks[i].timstamp);
    }
}

packets parse_workload(char *path)
{
    FILE *fptr;
    char *line = NULL;
    size_t len = 0;
    ssize_t read;

    fptr = fopen(path, "r");
    if (fptr == NULL)
    {
        fprintf(stderr, "Error opening file: %s\n", path);
        exit(EXIT_FAILURE);
    }

    packets pks;
    pks.num = 0;
    pks.pks = (packet *)malloc(pks.num * sizeof(packet));

    while ((read = getline(&line, &len, fptr)) != -1)
    {
        packet temp;
        temp = packet_from_line(line);
        pks.pks = realloc(pks.pks, (pks.num + 1) * sizeof(packet));
        pks.pks[pks.num] = temp;
        pks.num++;
    }

    return pks;
}

packet packet_from_line(char *line)
{
    packet pkt;
    char *word;
    int col;

    line[strcspn(line, "\n")] = 0; // stripping new line

    word = strtok(line, " ");
    col = 0;
    while (word != NULL)
    {
        switch (col)
        {
        case 0: // unique id
            pkt.id = atoi(word);
            break;
        case 1: // src
            pkt.src = atoi(word);
            break;
        case 2: // dest
            pkt.dest = atoi(word);
            break;
        case 3: // packet size
            pkt.size = atof(word);
            break;
        case 4: // timestamp
            pkt.timstamp = atof(word);
            break;
        }
        word = strtok(NULL, " ");
        col += 1;
    }

    return pkt;
}