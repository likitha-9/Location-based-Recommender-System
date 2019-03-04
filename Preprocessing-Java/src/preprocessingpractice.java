import java.io.File;
import java.io.FileNotFoundException;
//import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.text.SimpleDateFormat;
//import java.text.SimpleDateFormat;
import java.util.*;
public class preprocessingpractice {
 
	private static Scanner sc,sc1;

public static void main(String[] args) throws FileNotFoundException {
		// TODO Auto-generated method stub
		String directoryName="C:\\cabspottingdata\\cabspottingdata";
		File folder = new File(directoryName);
		File[] listOfFiles = folder.listFiles();
		//String content="";
		//System.out.println("list"+listOfFiles.length+"\n");
		String fileinput="C:\\cabspottingdata\\preprocessing";
	    
	    try
	    {
	    //FileWriter fw = new FileWriter("C:\\cabspottingdata\\preprocessing",true);
	    PrintWriter printer = new PrintWriter(fileinput);
	    int count=0;
		for (int i = 0; i < listOfFiles.length; i++) {
	      if (listOfFiles[i].isFile()) {
	    	String filename=directoryName+"\\"+listOfFiles[i].getName();
	        File file = new File(filename);
	    	sc = new Scanner(file);
			int c=0,sum=0;
			long max=0,min=0;
			
			while (sc.hasNextLine())
			{
				String line=sc.nextLine();
				//StringTokenizer st=StringTokenizer(line,"")
				String st[]=line.split(" ");
				if(c==0)
					min=Long.parseLong(st[3]);
				c++;
				sum=sum+Integer.parseInt(st[2]);
				if(Long.parseLong(st[3])>max)
					max=Long.parseLong(st[3]);
				if(Long.parseLong(st[3])<min)
					min=Long.parseLong(st[3]);
				//content=content+"\n"+line;
			}
			long diff=max-min;
			float hrs=(float)diff/3600;
			float occrate=(float)sum/c;
			if(occrate>=0.5 && hrs>=500)
			{
				String str=filename+" occupancy rate "+occrate+" No.of hrs travelled "+hrs;
				System.out.println(str);
				printer.write(str+"\n");
				count++;
			}
	      } 
	    }
		System.out.println(count);
		printer.close();
	    }
	    catch(IOException e)
	    {
	    	e.printStackTrace();
	    }
	    
	    try
	    {
		File input_file=new File(fileinput);
		sc = new Scanner(input_file);
		String fileinput1="C:\\cabspottingdata\\preprocessing1.txt";
	    int c=0;
		PrintWriter printer1 = new PrintWriter(fileinput1);
	    while (sc.hasNextLine())
		{
			String line=sc.nextLine();
			//StringTokenizer st=StringTokenizer(line,"")
			String st[]=line.split(" ");
			//int time=Integer.parseInt(st[3]);
			//System.out.println(time);
			String file_name=st[0];
			System.out.println(file_name+" ");
			File file=new File(file_name);
			sc1 = new Scanner(file);
			
			while(sc1.hasNextLine())
			{
				String l=sc1.nextLine();
				String s[]=l.split(" ");
				
				
				Date date = new Date(Long.parseLong(s[3])*1000L); 
				// format of the date
				SimpleDateFormat jdf = new SimpleDateFormat("yyyy-MM-dd HH:MM:ss");
				jdf.setTimeZone(TimeZone.getTimeZone("GMT-0"));
				String java_date = jdf.format(date);
				String d[]=java_date.split(" ");
				String time[]=d[1].split(":");
				if((time[0].equals("14")||(time[0].equals("15")&&time[1].equals("00")&&time[1].equals("00"))))
				{
					//System.out.println(" "+s[0]+" "+s[1]+" "+s[2]+" "+java_date+"\n");
					printer1.write(file_name+" "+l+"\n");
					c++;
				}
				
			}
		}
	    System.out.println(c);
	    printer1.close();
	    }
	    catch(IOException e)
	    {
	    	e.printStackTrace();
	    }
}
}
