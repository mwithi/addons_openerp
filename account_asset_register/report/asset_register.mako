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
  		
  		tr.subtotal td {
  			font-weight: bold;
  			line-height: 20px;
			border-top: 1px solid;
		    border-bottom: 2px solid;
		}
		
		tr.total td {
  			font-weight: bold;
  			line-height: 20px;
			border-top: 1px solid;
		    border-bottom: double;
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
                %endfor
            </td>
        </tr>
    </table>

    <table style="width: 100%; font-size: 12px;">
        <tr>
        	<th class="labels"> ID </th>
            <th width="8%" class="labels"> Code </th>
            <th width="20%" class="labels"> Name </th>
            <th> Purchase<br />Date </th>
            <th> Depreciation<br /> Start Date </th>
            <th width="8%" class="values"> Purchase Price</th>
            <th width="8%" class="values"> Revaluated / Devaluated<br />Value</th>
            <th width="8%" class="values"> Accumulated Depreciation</th>
            <th width="8%" class="values"> Accumulated Depreciation Previous Years</th>
            <th width="8%" class="values"> Depreciation Current Year</th>
            <th width="8%" class="values"> Depreciation Monthly Period </th>
            <th width="8%" class="values"> Net Book Value</th>
        </tr>
        %for line in lines():
        	%if line['type'] == 'category':
	        	<tr class="category">
	        		<td></td>
	    			<td colspan="11">${line['category']}</td>
	    		</tr>
			%elif line['type'] == 'asset':
				<tr>
	        		<td>${line['id']}</td>
	        		<td>${line['code']}</td>
	        		<td>${line['asset']}</td>
	        		%if line['date_purchase']:
	        			<td class="dates">${line['date_purchase']}</td>
					%else:
					    <td></td>
					%endif
	        		<td class="dates">${line['date_start']}</td>
	        		<td class="values">${line['asset_value']}</td>
	        		%if line['revaluated_value']:
	        			<td class="values">${line['revaluated_value']}</td>
					%else:
					    <td></td>
					%endif
	        		<td class="values">${line['accumulated_depreciation']}</td>
	        		<td class="values">${line['accumulated_depreciation_previous_years']}</td>
	        		<td class="values">${line['depreciation_current_year']}</td>
	        		<td class="values">${line['depreciation_monthly_period']}</td>
	        		<td class="values">${line['net_value']}</td>
	        	</tr>
        	%elif line['type'] == 'subtotal':
	        	<tr class="subtotal">
	        		<td></td>
	        		<td>Sub-Total</td>
	        		<td>${line['category']}</td>
	        		<td></td>
					<td></td>
	        		<td class="values">${line['asset_value']}</td>
	        		%if line['revaluated_value']:
	        			<td class="values">${line['revaluated_value']}</td>
					%else:
					    <td></td>
					%endif
	        		<td class="values">${line['accumulated_depreciation']}</td>
	        		<td class="values">${line['accumulated_depreciation_previous_years']}</td>
	        		<td class="values">${line['depreciation_current_year']}</td>
	        		<td class="values">${line['depreciation_monthly_period']}</td>
	        		<td class="values">${line['net_value']}</td>
	        	</tr>
	        	<tr class="space"><td colspan="13">&nbsp</td></tr>
    		%elif line['type'] == 'total':
	        	<tr class="total">
	        		<td></td>
	        		<td>Total</td>
	        		<td></td>
	        		<td></td>
					<td></td>
	        		<td class="values">${line['asset_value']}</td>
	        		%if line['revaluated_value']:
	        			<td class="values">${line['revaluated_value']}</td>
					%else:
					    <td></td>
					%endif
	        		<td class="values">${line['accumulated_depreciation']}</td>
	        		<td class="values">${line['accumulated_depreciation_previous_years']}</td>
	        		<td class="values">${line['depreciation_current_year']}</td>
	        		<td class="values">${line['depreciation_monthly_period']}</td>
	        		<td class="values">${line['net_value']}</td>
	        	</tr>
	        	<tr class="space"><td colspan="13">&nbsp</td></tr>
    		%endif
        %endfor
    </table>
</body>
</html>
