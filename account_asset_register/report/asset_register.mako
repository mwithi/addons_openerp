<!DOCTYPE html>
<html>
<head>
    <style type="text/css">
        ${css}
        
        body {
		    font-size: xx-small;
		}

		table {
		    border-spacing: 0px;
		    page-break-inside: auto
		}
		
		table tr {
            page-break-inside: avoid; 
            page-break-after: auto;
  		}
  		
  		tr.subtotal td {
  			font-weight: bold;
  			line-height: 20px;
			border-top: 1px solid black;
		    border-bottom: 2px solid black;
		}
		
		tr.total td {
  			font-weight: bold;
  			line-height: 20px;
			border-top: 1px solid black;
		    border-bottom: double black;
		}
		
		tr.space td {
  			line-height: 20px;
		}
		
		.values {
			text-align: right;
		}
		
		.dates {
			text-align: center;
		}
		
		.labels {
			text-align: left;
		}
		
		tr.category td {
			line-height: 20px;
			font-weight: bold;
		}
		
		.posted {
			text-align: right;
			color: black;
		}
		
		.unposted {
			text-align: right;
			color: blue;
			border: red;
		}
		
    </style>
</head>
<body>
    <%page expression_filter="entity"/>
    <br />
    <h1><b><i>Fixed Assets Register (Book Depreciation)</i></b></h1>
    <%
    """
    print "IN REPORT!"
    print objects, dir(objects)
    print "*************** LOCALS:"
    pp(locals())
    print datelines()
    print lines()
    """
    %>

    <table style="width: 100%" border="0">
        <tr class="table_header">
            <td colspan="3" height="30px">
                %for date in datelines():
                    Fiscal Year: ${date['fiscal_year']} (Values: ${date['currency']})
                    <br />
                    Unposted in blue
                %endfor
            </td>
        </tr>
    </table>

    <table style="width: 100%; font-size: 12px;">
        <tr>
        	<th class="labels">ID</th>
            <th width="7%" class="labels">Code</th>
            <th width="13%" class="labels">Name</th>
            <th>Depreciation<br />Start Date</th>
            <th width="7%" class="values">Opening<br />Value</th>
            <th width="7%" class="values">Increases</th>
            <th width="7%" class="values">Decreases</th>
            <th width="8%" class="values">Gross Book<br />Value</th>
            <th width="7%" class="values">Sales</th>
            <th width="7%" class="values">Profit / (Loss)<br />on Disposal</th>
            <th width="7%" class="values">Accumulated Depreciation<br />Previous Years</th>
            <th width="7%" class="values">Depreciation Current Year</th>
            <th width="7%" class="values">Write off<br />Accumulated Depreciation</th>
            <th width="7%" class="values">Total Depreciation</th>
            <th width="8%" class="values">Net Book<br />Value</th>
        </tr>
        %for line in lines():
        	%if line['type'] == 'category':
	        	<tr class="category">
	        		<td></td>
	    			<td colspan="14">${line['category']}</td>
	    		</tr>
			%elif line['type'] == 'asset':
				<tr>
	        		<td>${line['id']}</td>
	        		<td>${line['code']}</td>
	        		<td>${line['asset']}</td>
	        		<td class="dates">${line['date_start']}</td>
	        		<td class="values">${line['opening_cost']}</td>
	        		<td class="values">${line['revaluation']}</td>
	        		<td class="values">${line['devaluation']}</td>
	        		<td class="values">${line['gross_book_value']}</td>
	        		<td class="values">${line['sale_value']}</td>
	        		<td class="values">${line['profit_loss_disposal']}</td>
	        		%if line['previous_posted']:
	        			<td class="values">${line['accumulated_depreciation_previous_years']}</td>
	        		%else:
	        			<td class="unposted">${line['accumulated_depreciation_previous_years']}</td>
	        		%endif
	        		%if line['current_posted']:
	        			<td class="values">${line['depreciation_current_year']}</td>
	        		%else:
	        			<td class="unposted">${line['depreciation_current_year']}</td>
	        		%endif
	        		<td class="values">${line['write_off_accumulated_depreciation']}</td>
	        		<td class="values">${line['accumulated_depreciation']}</td>
	        		<td class="values">${line['net_value']}</td>
	        	</tr>
        	%elif line['type'] == 'subtotal':
	        	<tr class="subtotal">
	        		<td></td>
	        		<td>Sub-Total</td>
	        		<td colspan="2">${line['category']}</td>
	        		<td class="values">${line['opening_cost']}</td>
	        		<td class="values">${line['revaluation']}</td>
	        		<td class="values">${line['devaluation']}</td>
	        		<td class="values">${line['gross_book_value']}</td>
	        		<td class="values">${line['sale_value']}</td>
	        		<td class="values">${line['profit_loss_disposal']}</td>
	        		%if line['previous_posted']:
	        			<td class="values">${line['accumulated_depreciation_previous_years']}</td>
	        		%else:
	        			<td class="unposted">${line['accumulated_depreciation_previous_years']}</td>
	        		%endif
	        		%if line['current_posted']:
	        			<td class="values">${line['depreciation_current_year']}</td>
	        		%else:
	        			<td class="unposted">${line['depreciation_current_year']}</td>
	        		%endif
	        		<td class="values">${line['write_off_accumulated_depreciation']}</td>
	        		<td class="values">${line['accumulated_depreciation']}</td>
	        		<td class="values">${line['net_value']}</td>
	        	</tr>
	        	<tr class="space"><td colspan="13">&nbsp</td></tr>
    		%elif line['type'] == 'total':
	        	<tr class="total">
	        		<td></td>
	        		<td>Total</td>
	        		<td></td>
					<td></td>
	        		<td class="values">${line['opening_cost']}</td>
	        		<td class="values">${line['revaluation']}</td>
	        		<td class="values">${line['devaluation']}</td>
	        		<td class="values">${line['gross_book_value']}</td>
	        		<td class="values">${line['sale_value']}</td>
	        		<td class="values">${line['profit_loss_disposal']}</td>
	        		%if line['previous_posted']:
	        			<td class="values">${line['accumulated_depreciation_previous_years']}</td>
	        		%else:
	        			<td class="unposted">${line['accumulated_depreciation_previous_years']}</td>
	        		%endif
	        		%if line['current_posted']:
	        			<td class="values">${line['depreciation_current_year']}</td>
	        		%else:
	        			<td class="unposted">${line['depreciation_current_year']}</td>
	        		%endif
	        		<td class="values">${line['write_off_accumulated_depreciation']}</td>
	        		<td class="values">${line['accumulated_depreciation']}</td>
	        		<td class="values">${line['net_value']}</td>
	        	</tr>
	        	<tr class="space"><td colspan="13">&nbsp</td></tr>
    		%endif
        %endfor
    </table>
</body>
</html>
