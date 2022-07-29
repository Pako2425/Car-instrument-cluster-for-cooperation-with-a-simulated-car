#include <SPI.h>
#include <mcp2515.h>

struct can_frame lights_on;
MCP2515 mcp2515(10);

char message[10];
int firstByte;
  
void setup() {
  lights_on.can_id = 0x0F6;
  lights_on.can_dlc = 8;
  lights_on.data[0] = 0x00;
  lights_on.data[1] = 0x00;
  lights_on.data[2] = 0x00;
  lights_on.data[3] = 0x00;
  lights_on.data[4] = 0x00;
  lights_on.data[5] = 0x00;
  lights_on.data[6] = 0x00;
  lights_on.data[7] = 0x00;
  
  Serial.begin(9600);

  mcp2515.reset();
  mcp2515.setBitrate(CAN_125KBPS, MCP_8MHZ);
  mcp2515.setNormalMode();

  firstByte = 0;
}

void rBinNum(char* tab)
{
  char charIn;
  for(int i = 0; i < 8; i++)
  {
    charIn = Serial.read();
    tab[i] = charIn;
  }
  Serial.read();
}

int binStrToInt(char *binTab)
{
  int iValue = 0;
  for(int charIndex = 0; charIndex < 8; charIndex++)
  {
    if(binTab[7-charIndex] == '1')
    {
      iValue = iValue + (1<<charIndex);
    }
    else
    {
      iValue = iValue;
    }
  }
  return iValue;
}

void loop() {
  ///////////------------szukanie bitow odpowiedzialnych za zaswiecanie sie kontrolek--------/////////////////////
  /*
  for(int i = 0; i < 255; i++)
  {
    lights_on.data[1] = i;
    mcp2515.sendMessage(&lights_on);
    Serial.print(lights_on.data[1], BIN);
    Serial.print("\n");
    delay(250);
  }
  delay(200);
  */

  ///-------------------------------------------------------------------------------------------------------
  
  int x = Serial.available();
  if(x > 0)
  {
    rBinNum(message);
    firstByte = binStrToInt(message);
  }
  lights_on.data[0] = firstByte;
  mcp2515.sendMessage(&lights_on);
  delay(500);
  
}
