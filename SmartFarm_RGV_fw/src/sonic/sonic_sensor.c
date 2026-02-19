#include "sonic_sensor.h"

#define TRIG 6
#define ECHO 7
#define SOUND_VELOCITY 340UL


int sonic_sensor(void)
{
	unsigned int distance;


	TCCR1B = 0x03;
	PORTE &= ~(1<<TRIG);
	_delay_us(10);
	PORTE |= (1<<TRIG);
	_delay_us(10);
	PORTE &= ~(1<<TRIG);
	while(!(PINE & (1<<ECHO)));
	TCNT1 = 0x0000;
	while(PINE & (1<<ECHO));
	TCCR1B = 0x00;
	distance = (unsigned int)(SOUND_VELOCITY * (TCNT1 * 4 / 2) / 1000);

	return distance;
}