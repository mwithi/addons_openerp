<!DOCTYPE html>
<html>
<head>
    <style type="text/css">
        ${css}
		table {
		    border-spacing: 0px;
		    page-break-inside: auto
		}
		
		table tr {
                page-break-inside: avoid; 
                page-break-after: auto;
  		}
		
		table, td, th {
		    border: 1px dotted black;
		}
		
		.none {
			border: 0px;
		}
		
		.section {
			border: 0px;
			font-size: large;
		}
		
		.title {
			border: 0px;
			font-size: medium;
		}
		
		.title_children {
			border: 0px;
			font-size: small;
		}
		
		.subtitle {
			border: 0px;
			font-size: small;
		}
		
		.total {
			border: 2px solid black;
		}
		
		.empty {
			border: 0px;
			border-left: 1px dotted black;
			border-right: 1px dotted black;
		}
		
		.emptyfy {
			border: 0px;
			border-left: 2px solid black;
			border-right: 2px solid black;
		}
		
		.endfy {
			border: 0px;
			border-left: 2px solid black;
			border-right: 2px solid black;
			border-bottom: 2px solid black;
		}
		
		.fy {
			border-left: 2px solid black;
			border-right: 2px solid black;
		}
		
		.posted {
			color: black;
		}
		
		.unposted {
			color: blue;
		}
		
    </style>
</head>
<body>
    <%page expression_filter="entity"/>
    <h1><b><i>Treasury Budget / Cash Flows Monthly Report</i></b></h1>
    <%
    """
    print "IN REPORT!"
    print objects, dir(objects)
    print "*************** LOCALS:"
    pp(locals())
    print date_lines()
    print lines()
    """
    %>
    
    <%def name="indent(level, title)">
	    ${"-" * level + " " * level * 4}${title}
	</%def>
    
    <table style="width: 100%" border="0">
        <tr class="table_header">
            <td colspan="3" height="30px">
                %for date in datelines():
                    Fiscal Year: ${date['fiscal_year']} (Values: ${date['divisor']} ${date['currency']})
                    %if date['target'] == 'all':
                    	<br />
                    	Unposted in blue
                    %endif
                %endfor
            </td>
        </tr>
    </table>

    <table style="width: 100%; font-size: 12px; border: 1px dotted;">
        <tr>
            <th> Ledger Position </th>
            <th> Account </th>
            <th> July </th>
            <th> August </th>
            <th> September </th>
            <th> October </th>
            <th> November </th>
            <th> December </th>
            <th> January </th>
            <th> February </th>
            <th> March </th>
            <th> April </th>
            <th> May </th>
            <th> June </th>
            <th class="total"> FY </th>
            <th> % </th>
        </tr>
        %for line in lines():
        	%if line['type'] == 'section':
			    <tr class="section">
			    
        	%elif line['type'] == 'title':
        		<tr class="title">  
        		
        	%elif line['type'] == 'total':
				<tr class="total">    
			
			%elif line['type'] == 'calc':
				<tr>
				
			%elif line['type'] == 'end':
				<tr>
				
    		%else:
   				<tr>

        	%endif
	        	%if line['type'] == 'section':
	        		<td colspan="14" class="section" height="50px"><strong>${line['title']}</strong></td>
	        		<td class="emptyfy"></td>
	        		
	        	%elif line['type'] == 'title':
	        		%if line['level'] == 0:
	        			<td colspan="14" class="title" height="40px"><strong>${indent(line['level'],line['title'])}</strong></td>
	        		%else:
	        			<td colspan="14" class="title_children" height="30px">${indent(line['level'],line['title'])}</td>
	        		%endif
	        		<td class="emptyfy"></td>
	        	
	        	%elif line['type'] == 'subtitle':
	        		<td class="empty"></td>
	        		<td colspan="13" class="subtitle"><strong>${line['title']}</strong></td>
	        		<td class="emptyfy"></td>
	        		
	        	%elif line['type'] == 'total':
	        		<td class="none" width="5%"></strong></td>
	        		<td width="25%"><strong>${line['title']}</strong></td>
	        	
	        	%elif line['type'] == 'calc':
	        		<td class="none" width="5%"></strong></td>
	        		<td width="25%">${line['title']}</td>
	        		
	        	%elif line['type'] == 'end':
	        		<td class="none" width="5%"></strong></td>
	        		<td width="25%">${line['title']}</td>
	        		
	        	%else:
	        		<td width="5%">${indent(line['level'],line['position'])}</td>
	        		<td width="25%">${line['title']}</td>
	        	%endif
        		%if line['type'] == 'value':
        			%if line['1_posted']:
	        			<td width="5%" align="right" class="posted">${line['1_locale']}</td>
	        		%else:
	        			<td width="5%" align="right" class="unposted">${line['1_locale']}</td>
	  				%endif
	  				%if line['2_posted']:
	        			<td width="5%" align="right" class="posted">${line['2_locale']}</td>
	        		%else:
	        			<td width="5%" align="right" class="unposted">${line['2_locale']}</td>
	  				%endif
	  				%if line['3_posted']:
	        			<td width="5%" align="right" class="posted">${line['3_locale']}</td>
	        		%else:
	        			<td width="5%" align="right" class="unposted">${line['3_locale']}</td>
	  				%endif
	  				%if line['4_posted']:
	        			<td width="5%" align="right" class="posted">${line['4_locale']}</td>
	        		%else:
	        			<td width="5%" align="right" class="unposted">${line['4_locale']}</td>
	  				%endif
	  				%if line['5_posted']:
	        			<td width="5%" align="right" class="posted">${line['5_locale']}</td>
	        		%else:
	        			<td width="5%" align="right" class="unposted">${line['5_locale']}</td>
	  				%endif
	  				%if line['6_posted']:
	        			<td width="5%" align="right" class="posted">${line['6_locale']}</td>
	        		%else:
	        			<td width="5%" align="right" class="unposted">${line['6_locale']}</td>
	  				%endif
	  				%if line['7_posted']:
	        			<td width="5%" align="right" class="posted">${line['7_locale']}</td>
	        		%else:
	        			<td width="5%" align="right" class="unposted">${line['7_locale']}</td>
	  				%endif
	  				%if line['8_posted']:
	        			<td width="5%" align="right" class="posted">${line['8_locale']}</td>
	        		%else:
	        			<td width="5%" align="right" class="unposted">${line['8_locale']}</td>
	  				%endif
	  				%if line['9_posted']:
	        			<td width="5%" align="right" class="posted">${line['9_locale']}</td>
	        		%else:
	        			<td width="5%" align="right" class="unposted">${line['9_locale']}</td>
	  				%endif
	  				%if line['10_posted']:
	        			<td width="5%" align="right" class="posted">${line['10_locale']}</td>
	        		%else:
	        			<td width="5%" align="right" class="unposted">${line['10_locale']}</td>
	  				%endif
	  				%if line['11_posted']:
	        			<td width="5%" align="right" class="posted">${line['11_locale']}</td>
	        		%else:
	        			<td width="5%" align="right" class="unposted">${line['11_locale']}</td>
	  				%endif
	  				%if line['12_posted']:
	        			<td width="5%" align="right" class="posted">${line['12_locale']}</td>
	        		%else:
	        			<td width="5%" align="right" class="unposted">${line['12_locale']}</td>
	  				%endif
	        		<td width="6%" align="right" class="fy">${line['13_locale']}</td>
	        		<td width="4%" align="right" >${line['14_locale']} &#37;</td>
	        	%elif line['type'] == 'total':
	        		<td width="5%" align="right"><strong>${line['1_locale']}</strong></td>
	        		<td width="5%" align="right"><strong>${line['2_locale']}</strong></td>
	        		<td width="5%" align="right"><strong>${line['3_locale']}</strong></td>
	        		<td width="5%" align="right"><strong>${line['4_locale']}</strong></td>
	        		<td width="5%" align="right"><strong>${line['5_locale']}</strong></td>
	        		<td width="5%" align="right"><strong>${line['6_locale']}</strong></td>
	        		<td width="5%" align="right"><strong>${line['7_locale']}</strong></td>
	        		<td width="5%" align="right"><strong>${line['8_locale']}</strong></td>
	        		<td width="5%" align="right"><strong>${line['9_locale']}</strong></td>
	        		<td width="5%" align="right"><strong>${line['10_locale']}</strong></td>
	        		<td width="5%" align="right"><strong>${line['11_locale']}</strong></td>
	        		<td width="5%" align="right"><strong>${line['12_locale']}</strong></td>
	        		<td width="6%" align="right" class="fy"><strong>${line['13_locale']}</strong></td>
	        		<td width="4%" align="right"><strong>${line['14_locale']}  &#37;</strong></td>
	        	%elif line['type'] == 'calc':
	        		<td width="5%" align="right">${line['1_locale']}</td>
	        		<td width="5%" align="right">${line['2_locale']}</td>
	        		<td width="5%" align="right">${line['3_locale']}</td>
	        		<td width="5%" align="right">${line['4_locale']}</td>
	        		<td width="5%" align="right">${line['5_locale']}</td>
	        		<td width="5%" align="right">${line['6_locale']}</td>
	        		<td width="5%" align="right">${line['7_locale']}</td>
	        		<td width="5%" align="right">${line['8_locale']}</td>
	        		<td width="5%" align="right">${line['9_locale']}</td>
	        		<td width="5%" align="right">${line['10_locale']}</td>
	        		<td width="5%" align="right">${line['11_locale']}</td>
	        		<td width="5%" align="right">${line['12_locale']}</td>
	        		<td width="6%" align="right" class="fy">${line['13_locale']}</td>
	        		<td width="4%" align="right">${line['14_locale']}</td>
	        	%elif line['type'] == 'end':
	        		<td width="5%" align="right">${line['1_locale']}</td>
	        		<td width="5%" align="right">${line['2_locale']}</td>
	        		<td width="5%" align="right">${line['3_locale']}</td>
	        		<td width="5%" align="right">${line['4_locale']}</td>
	        		<td width="5%" align="right">${line['5_locale']}</td>
	        		<td width="5%" align="right">${line['6_locale']}</td>
	        		<td width="5%" align="right">${line['7_locale']}</td>
	        		<td width="5%" align="right">${line['8_locale']}</td>
	        		<td width="5%" align="right">${line['9_locale']}</td>
	        		<td width="5%" align="right">${line['10_locale']}</td>
	        		<td width="5%" align="right">${line['11_locale']}</td>
	        		<td width="5%" align="right">${line['12_locale']}</td>
	        		<td width="6%" align="right" class="endfy">${line['13_locale']}</td>
	        		<td width="4%" align="right">${line['14_locale']}</td>
	        	%else:
	        		<!-- td colspan="14"></td -->
	        	%endif
        	</tr>
        %endfor
    </table>
    %for date in datelines():
        %if date['warning']:
        	<br />
	        <table width="50%">
	            %if len(excluded()) > 0:
		            <tr class="total">
		        		<td>WARNING!!! Some Ledger Positions are not included, please inform System Administrator</td>
		            </tr> 
		            %for account in excluded():
		            <tr>
		            	<td>${account['account_code']} - ${account['ref']} - ${account['note']}</td>
		            </tr>
		            %endfor
		        %endif
		    </table>
		    <br />
		    <table width="50%">
		        %if len(duplicated()) > 0:
			        <tr class="total">
		        		<td>WARNING!!! Some Ledger Positions are duplicated, please inform System Administrator</td>
		            </tr> 
		            %for account in duplicated():
		            <tr>
		            	<td>${account['account_code']} - ${account['ref']} - ${account['note']}</td>
		            </tr>
		            %endfor
		        %endif
	        </table>
    	%endif
   	%endfor
</body>
</html>
