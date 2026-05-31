import asyncio

MAX_CONCURRENT = 500 #not more than 500 connections at a time 

async def tcp_scan(target_ip, target_port, semaphore):
    async with semaphore:  #Restriction is coming first this is important
        try:
            reader, writer = await asyncio.wait_for( #Reader and Writer are 2 objects which are used to read and write response to the server we are communicating with
                asyncio.open_connection(target_ip, target_port), #Socket is created behind the scene
                timeout=3)
            print(f"[*]{target_port} is open") #If we managed to esablish connection the port is open isn't it 
            writer.close() #It is a good practice to close connection as long as we don't need them
            await writer.wait_closed() #We need to wait till it clossed 
        except asyncio.TimeoutError:
            pass
        except ConnectionRefusedError:
            pass



async def main():
    target_ip = input("\nWhat is your target's ip ?\n")
    print("Enter each port which you want to check one by one and then type end") #One of the ways using making list with ports which we need ,i won't use this type in big projects but it suits well this one
    target_ports = []
    while (True):
        n = input("\nPort or end\n")
        if n.lower() == "end":
            break
        else:
            target_ports.append(int(n))
    

    
    semaphore = asyncio.Semaphore(MAX_CONCURRENT) #We are putting variable which is higher here so it can control our threads
     #And here we go launching our scan with all parametres
    tasks = [tcp_scan(target_ip, port, semaphore) for port in target_ports] 
    await asyncio.gather(*tasks)

    
asyncio.run(main())


















