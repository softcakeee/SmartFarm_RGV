#define F_CPU 16000000UL
#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h>
#include <stdio.h>

#define Fast_Front 0xFA
#define Slow_Front 0xF7
#define Fast_Back  0xF9
#define Slow_Back 0xEF
#define STOP 0xFF


#define UP 0xFC
#define DOWN 0xF3

void SET_UP(void);

void UART1_init(void);
void UART1_transmit(char data);
void UART1_Transmit_String(char *str);
unsigned char UART1_receive(void);



volatile int rxbuff ;
volatile int s;
volatile int ms;
volatile int stack = 0;
unsigned int distance;


volatile int A = 0;
#define ABC 5;

volatile int qwer = 0;

int asd = 0;


void UART1_init(void)
{
	UCSR1A=0b00100000;
	UCSR1B=0b10011000; // 송신 수신 활성화
	UCSR1C=0b00000110; // 비동기 , No parity , 8bit data, 1 stop bit
	
	UBRR1H=0;
	UBRR1L=103; // baud rate : 9600 설정
}

void SET_UP(void)
{

	
	DDRB = 0xFF;
	DDRC = 0xFF;
	
	PORTB = 0xFF;
	PORTC = 0xFF;

	
	UART1_init();
	sei();
	
}


void UART1_transmit(char data)
{
	while(!(UCSR1A & (1<<UDRE1)));
	UDR1 = data;
}

void UART1_Transmit_String(char *str)
{
	//문자열이 null이 될때 까지
	while(*str != '\0'){
		UART1_transmit(*str++); // 문자 출력
	}
}

unsigned char UART1_receive(void)
{
	while(!(UCSR1A & (1<<RXC1)));
	return UDR1;
}

void RGV_UART(void)
{	switch(rxbuff)
	{
		case 'A' :
		PORTB = Slow_Back;
		rxbuff = 0;
		break;

		case 'B' :
		PORTB = Slow_Front;
		rxbuff = 0;
		break;

		case 'C' :
		PORTB = Fast_Back;
		rxbuff = 0;
		break;

		case 'D' :
		PORTB = Fast_Front;
		rxbuff = 0;
		break;

		case 'E' :
		PORTC = UP;
		rxbuff = 0;
		break;

		case 'F' :
		PORTC = DOWN;
		rxbuff = 0;
		break;
		
		case 'Z' :
		PORTB = STOP;
		PORTC = STOP;
		rxbuff = 0;
		break;
		
		
	}
}

ISR(USART1_RX_vect){
	//rxbuff = UDR1;
	
	rxbuff = UART1_receive();
}




int main(){
	
	
	SET_UP();

	
	while(1)
	{

		//RGV_UART();
		PORTB = 0x00;
		_delay_ms(1000);
		PORTB = 0xFF;
		
	}
}